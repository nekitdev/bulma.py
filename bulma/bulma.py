from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, MutableSequence, Optional, Set, TypeVar, Union

import sass  # type: ignore

__all__ = (
    "FIND",
    "NESTED",
    "EXPANDED",
    "COMPACT",
    "COMPRESSED",
    "Compiler",
    "Include",
    "run",
)

# names and stuff related to paths
PATH = Path(__file__).parent
BULMA = "bulma"
BULMA_CSS = "bulma.css"
THEME_CSS = "{theme}_bulma.css"

CUSTOM = "custom"

DIST = "dist"

ALL = "_all"

DEMO = "demo"

EXTENSIONS = "extensions"

FUNCTIONS = "functions"
INITIAL_VARIABLES = "initial-variables"

INITIAL = (INITIAL_VARIABLES, FUNCTIONS)
MOVED = {"animations"}

UTILITIES = "utilities"

CSS = "css"
JS = "js"
SASS = "sass"
SCSS = "scss"

# empty string and newline to use
DOT = "."
EMPTY = ""
UNDERSCORE = "_"
NEWLINE = "\n"


def is_private(string: str) -> bool:
    return string.startswith(UNDERSCORE)


def get_name(name: str) -> str:
    name, dot, rest = name.partition(DOT)

    return name


# simple code templates we are going to use

UTF_8 = "utf-8"
CHARSET = f"@charset {UTF_8!r};"
IMPORT = "@import {path!r};"
VARIABLE = "${name}: {value};"

# other things used in different utilities
SASS_PATTERNS = (  # relative path in the extension -> glob pattern
    (Path("src/sass"), "_all.sass"),
    (Path("src/sass"), "index.sass"),
    (Path("src/sass"), "*.sass"),
    (Path("src"), "*.s[ac]ss"),
    (Path("dist"), "*.sass"),
    (Path("dist"), "*.min.css"),
    (Path("dist"), "*.css"),
    (Path(""), "*.s[ac]ss"),
)

MIN_JS_PATTERN = "*.min.js"
JS_PATTERN = "*[!min].js"

CSS_SUFFIX = ".css"
TEST_SUFFIX = ".test"

# different output styles
NESTED = "nested"
EXPANDED = "expanded"
COMPACT = "compact"
COMPRESSED = "compressed"

# if all extensions need to be imported, we pass FIND
FIND = "find"

# theme variables
THEME_VARIABLES = "{theme}_variables"


T = TypeVar("T")


def unique(iterable: Iterable[T]) -> Iterator[T]:
    seen: Set[T] = set()

    add_to_seen = seen.add

    for item in iterable:
        if item not in seen:
            add_to_seen(item)

            yield item


def run(iterator: Iterator[T]) -> None:
    for _ in iterator:
        pass


INCLUDE_CSS = """
<link rel="preload" href="{css}" as="style">
<link rel="stylesheet" href="{css}">
""".strip()

INCLUDE_JS = """
<script defer src="{js}"></script>
""".strip()


IT = TypeVar("IT", bound="Include")


class Include:
    def __init__(
        self,
        themes: MutableSequence[str],
        custom: MutableSequence[str],
        script: MutableSequence[str],
        static: Optional[Union[str, Path]] = None,
    ) -> None:
        self.themes = themes
        self.custom = custom
        self.script = script

        if static is None:
            static = Path()

        self.static = Path(static)

    def with_static(self: IT, static: Union[str, Path]) -> IT:
        self.static = Path(static)

        return self

    def get_path(self, path: str) -> Path:
        return self.static / path

    def include_css_relative(self, css: str) -> str:
        return self.include_css(self.get_path(css).as_posix())

    def include_css(self, css: str) -> str:
        return INCLUDE_CSS.format(css=css)

    def include_js_relative(self, js: str) -> str:
        return self.include_js(self.get_path(js).as_posix())

    def include_js(self, js: str) -> str:
        return INCLUDE_JS.format(js=js)

    def find_theme_relative(self, theme: Optional[str] = None) -> str:
        if theme is None:
            name = BULMA_CSS

        else:
            name = THEME_CSS.format(theme=theme)

        for file in self.themes:
            if Path(file).name == name:
                return file

        raise RuntimeError(f"Can not find {theme!r} theme.")

    def find_theme(self, theme: Optional[str] = None) -> str:
        return self.get_path(self.find_theme_relative(theme)).as_posix()

    def include_theme(self, theme: Optional[str] = None) -> str:
        return self.include_css_relative(self.find_theme_relative(theme))

    def generate_custom(self) -> Iterator[str]:
        yield from map(self.include_css_relative, self.custom)

    def include_custom(self) -> str:
        return NEWLINE.join(self.generate_custom())

    def generate_script(self) -> Iterator[str]:
        yield from map(self.include_js_relative, self.script)

    def include_script(self) -> str:
        return NEWLINE.join(self.generate_script())

    def generate_all(self, theme: Optional[str] = None) -> Iterator[str]:
        yield self.include_theme(theme)
        yield from self.generate_custom()
        yield from self.generate_script()

    def include_all(self, theme: Optional[str] = None) -> str:
        return NEWLINE.join(self.generate_all(theme))


class Compiler:
    def __init__(
        self,
        extensions: Union[str, Iterable[str]] = (),  # extensions to load
        themes: Iterable[str] = (),  # themes to use
        variables: Optional[Dict[str, Any]] = None,  # variables to use globally
        override: str = EMPTY,  # sass or scss string to add after bulma imports
        minified: bool = True,  # whether to prefer minified javascript files
        output_style: str = NESTED,  # style for compilation output
        custom: Iterable[str] = (),  # custom files to compile and include
        **settings: Any,  # other settings to apply
    ) -> None:
        self._settings = settings

        if variables is None:
            variables = {}

        self._extensions = extensions
        self._themes = themes

        self._variables = variables

        self._override = override

        self._minified = minified
        self._output_style = output_style

        self._custom = custom

        self._path = PATH
        self._bulma_path = PATH / BULMA / SASS

    @property
    def path(self) -> Path:
        return self._path

    @property
    def bulma_path(self) -> Path:
        return self._bulma_path

    @property
    def settings(self) -> Dict[str, Any]:
        return self._settings

    @property
    def extensions(self) -> Iterable[str]:
        extensions = self._extensions

        if extensions == FIND:
            extensions = list(self.generate_extensions())

        return extensions

    def generate_extensions(self) -> Iterator[str]:
        for extension in (self.path / EXTENSIONS).iterdir():
            yield extension.name

    def is_enabled(self, extension: str) -> bool:
        return extension in self.extensions

    def is_enabled_path(self, extension_path: Path) -> bool:
        return self.is_enabled(extension_path.name)

    @property
    def custom(self) -> Iterable[str]:
        return self._custom

    @property
    def variables(self) -> Dict[str, Any]:
        return self._variables

    @property
    def themes(self) -> Iterable[str]:
        return self._themes

    def get_theme_variables(self, theme: str) -> Dict[str, Any]:
        return self.settings.get(THEME_VARIABLES.format(theme=theme), {})

    @property
    def output_style(self) -> str:
        return self._output_style

    @property
    def minified(self) -> bool:
        return self._minified

    @property
    def override(self) -> str:
        return self._override

    def generate_variables(self, variables: Dict[str, Any]) -> Iterator[str]:
        for name, value in variables.items():
            yield VARIABLE.format(name=name, value=value)

    def get_bulma_imports(self) -> Iterator[str]:
        for path in self.bulma_path.iterdir():
            if path.is_dir() and path.name != UTILITIES:
                yield IMPORT.format(path=(path / ALL).relative_to(self.path).as_posix())

    def get_bulma_initial(self) -> Iterator[str]:
        for name in INITIAL:
            yield IMPORT.format(
                path=(self.bulma_path / UTILITIES / name).relative_to(self.path).as_posix()
            )

    def get_bulma_derived(self) -> Iterator[str]:
        exclude = set(INITIAL) | MOVED

        for path in (self.bulma_path / UTILITIES).iterdir():
            name = get_name(path.name)

            if name not in exclude:
                yield IMPORT.format(
                    path=(self.bulma_path / UTILITIES / name).relative_to(self.path).as_posix()
                )

    def get_extension_imports(self) -> Iterator[str]:
        for extension in (self.path / EXTENSIONS).iterdir():
            if self.is_enabled_path(extension):
                for path in self.get_sass_files(extension):
                    yield IMPORT.format(path=path.relative_to(self.path).as_posix())

    def generate_theme(self, theme: Optional[str] = None) -> Iterator[str]:
        variables = self.variables.copy()

        if theme is not None:
            variables.update(self.get_theme_variables(theme))

        yield CHARSET
        yield EMPTY
        yield from self.get_bulma_initial()
        yield EMPTY
        yield from self.generate_variables(variables)
        yield EMPTY
        yield from self.get_bulma_derived()
        yield EMPTY
        yield from self.get_bulma_imports()
        yield EMPTY
        yield from self.override.splitlines()
        yield EMPTY
        yield from self.get_extension_imports()
        yield EMPTY

    def generate_themes(self) -> Iterator[Iterator[str]]:
        yield self.generate_theme()

        for theme in self.themes:
            yield self.generate_theme(theme)

    def compile_theme(self, theme: Optional[str] = None) -> str:
        source = NEWLINE.join(self.generate_theme(theme))

        string: str = sass.compile(
            string=source, output_style=self.output_style, include_paths=[self.path.as_posix()]
        )

        return string

    def compile_themes(self) -> Iterator[str]:
        yield self.compile_theme()

        for theme in self.themes:
            yield self.compile_theme(theme)

    def save_theme(
        self, theme: Optional[str] = None, root: Optional[Union[str, Path]] = None
    ) -> Path:
        output = self.compile_theme(theme)

        if root is None:
            root = self.path

        root = Path(root)

        (root / CSS).mkdir(exist_ok=True)  # make sure the directory is created

        if theme is None:
            path = root / CSS / BULMA_CSS

        else:
            path = root / CSS / THEME_CSS.format(theme=theme)

        path.write_text(output, encoding=UTF_8)

        return path

    def save_theme_relative(
        self, theme: Optional[str] = None, root: Optional[Union[str, Path]] = None
    ) -> str:
        if root is None:
            root = self.path

        return self.save_theme(theme, root).relative_to(root).as_posix()

    def save_themes(
        self, root: Optional[Union[str, Path]] = None
    ) -> Iterator[Path]:
        yield self.save_theme(None, root)

        for theme in self.themes:
            yield self.save_theme(theme, root)

    def save_themes_relative(
        self, root: Optional[Union[str, Path]] = None
    ) -> Iterator[str]:
        if root is None:
            root = self.path

        for theme in self.save_themes(root):
            yield theme.relative_to(root).as_posix()

    def save_required_js_files(self, root: Optional[Union[str, Path]] = None) -> Iterator[Path]:
        if root is None:
            root = self.path

        root = Path(root)

        (root / JS).mkdir(exist_ok=True)  # make sure we have the directory created

        for source in self.get_required_js_files():
            destination = root / JS / source.name

            destination.touch()

            destination.write_text(source.read_text(UTF_8), UTF_8)

            yield destination

    def save_required_js_files_relative(
        self, root: Optional[Union[str, Path]] = None
    ) -> Iterator[str]:
        if root is None:
            root = self.path

        for path in self.save_required_js_files(root):
            yield path.relative_to(root).as_posix()

    def compile_path(self, path: Union[str, Path]) -> str:
        string: str = sass.compile(
            string=IMPORT.format(path=Path(path).as_posix(), output_style=self.output_style)
        )

        return string

    def compile_custom_css(self) -> Iterator[str]:
        for path in self.get_custom_files():
            yield self.compile_path(path)

    def save_custom_css(self, root: Optional[Union[str, Path]] = None) -> Iterator[Path]:
        if root is None:
            root = self.path

        root = Path(root)

        for path in self.get_custom_files():
            output = self.compile_path(path)

            path = (root / CUSTOM / path).with_suffix(CSS_SUFFIX)

            path.parent.mkdir(exist_ok=True)

            path.write_text(output, encoding=UTF_8)

            yield path

    def save_custom_css_relative(self, root: Optional[Union[str, Path]] = None) -> Iterator[str]:
        if root is None:
            root = self.path

        for path in self.save_custom_css(root):
            yield path.relative_to(root).as_posix()

    def save(self, root: Optional[Union[str, Path]] = None) -> Include:
        themes = list(self.save_themes_relative(root))
        custom = list(self.save_custom_css_relative(root))

        script = list(self.save_required_js_files_relative(root))

        return Include(themes=themes, custom=custom, script=script)

    def get_custom_files(self) -> Iterator[Path]:
        for path in self.custom:
            yield Path(path)

    def get_sass_files_dirty(self, extension_path: Path) -> Iterator[Path]:
        for relative_path, pattern in SASS_PATTERNS:
            for path in (extension_path / relative_path).rglob(pattern):
                if pattern.endswith(CSS_SUFFIX):
                    path = path.with_suffix(EMPTY)

                name = get_name(path.name)

                if (name == ALL or not is_private(name)) and name != DEMO:
                    yield path

    def get_sass_files(self, extension_path: Path) -> Iterator[Path]:
        return unique(self.get_sass_files_dirty(extension_path))

    def get_js_files(self, extension_path: Path) -> Iterator[Path]:
        path = extension_path / DIST

        files = (
            file for file in path.rglob(JS_PATTERN)
            if TEST_SUFFIX not in file.suffixes  # exclude test files
        )

        if self.minified:  # if we need to minify...
            minified_files = {
                get_name(minified_file.name): minified_file
                for minified_file in path.rglob(MIN_JS_PATTERN)
            }

            for file in files:  # ... go through normal files and yield minified versions, if found
                yield minified_files.get(get_name(file.name), file)

        else:
            yield from files

    def get_required_js_files(self) -> Iterator[Path]:
        for extension in (self.path / EXTENSIONS).iterdir():
            if self.is_enabled_path(extension):
                yield from self.get_js_files(extension)
