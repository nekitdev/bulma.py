from functools import wraps
from operator import attrgetter as get_attr
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Iterator, Optional, Set, TypeVar, Union

import sass  # type: ignore

__all__ = (
    "FIND",
    "NESTED",
    "EXPANDED",
    "COMPACT",
    "COMPRESSED",
    "Compiler",
    "Settings",
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
EXTENSIONS = "extensions"
UTILITIES = "utilities"

CSS = "css"
SASS = "sass"
SCSS = "scss"

# empty string and newline to use
EMPTY = ""
UNDERSCORE = "_"
NEWLINE = "\n"


def is_private(string: str) -> bool:
    return string.startswith(UNDERSCORE)


# simple code templates that we are going to use
COMMENT_VARIABLE = "/* theme variables */"
UTF_8 = "utf-8"
CHARSET = f"@charset {UTF_8!r};"
IMPORT = "@import {path!r};"
VARIABLE = "${name}: {value};"

# we should better preload our style sheet
INCLUDE_CSS = """
<link rel="preload" href="{css}" as="style">
<link rel="stylesheet" href="{css}">
""".strip()

# and scripts can be deferred so that the page can load nicely
INCLUDE_JS = """
<script defer type="text/javascript" src="{js}"></script>
""".strip()

# other things used in different utilities
SASS_PATTERNS = (  # relative path in the extension -> glob pattern
    (Path("src/sass"), "_all.sass"),
    (Path("src/sass"), "index.sass"),
    (Path("src/sass"), "*.sass"),
    (Path("src"), "*.s[ac]ss"),
    (Path("dist"), "*.sass"),
    (Path("dist"), "*.min.css"),
    (Path("dist"), "*.css"),
)

MIN_JS_PATTERN = "*.min.js"
JS_PATTERN = "*.js"

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


S = TypeVar("S", bound="Settings")


class Settings(Dict[str, Any]):
    def __getattr__(self, name: str) -> Any:
        if name in self:
            return self[name]

        raise AttributeError(name)

    def __setattr__(self, name: str, value: Any) -> None:
        self_dict = self.__dict__

        if name in self_dict:
            self_dict[name] = value

        else:
            self[name] = value

    def copy(self: S) -> S:
        return self.__class__(self)


SETTINGS = Settings(
    custom=[],  # custom files to compile and include
    extensions=[],  # extensions to load
    minified=True,  # whether to prefer minified javascript files
    themes=[],  # themes to use
    token="",  # font awesome token
    variables={},  # variables to use globally
    output_style=NESTED,  # style for compilation output
)


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


def cache_by(*names: str) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Cache function result by object's attributes given by names."""

    if not names:
        raise ValueError("@cache_by requires at least one name to be provided.")

    def decorator(function: Callable[..., T]) -> Callable[..., T]:
        get_attrs = tuple(get_attr(name) for name in names)

        name = function.__name__

        if not name.isidentifier():
            name = f"unnamed_{id(function):x}"

        cached_attr = f"_{name}_cached"
        cached_by_attr = f"_{name}_cached_by"

        @wraps(function)
        def wrapper(self, *args, **kwargs) -> T:
            actual = tuple(get_attr(self) for get_attr in get_attrs)

            try:
                cached = getattr(self, cached_attr)
                cached_by = getattr(self, cached_by_attr)

            except AttributeError:
                pass

            else:
                if actual == cached_by:
                    return cached

            result = function(self, *args, **kwargs)

            setattr(self, cached_attr, result)
            setattr(self, cached_by_attr, actual)

            return result

        return wrapper

    return decorator


class Compiler:
    def __init__(self, settings: Optional[Settings] = None) -> None:
        actual_settings = SETTINGS.copy()

        if settings:
            actual_settings.update(settings)

        self.settings = actual_settings

        self.path = PATH
        self.bulma_path = PATH / BULMA / SASS

    @property  # type: ignore
    @cache_by("settings.extensions")
    def extensions(self) -> Iterable[str]:
        extensions = self.settings.extensions

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
        return self.settings.custom

    @property
    def variables(self) -> Dict[str, Any]:
        return self.settings.variables

    @property
    def themes(self) -> Iterable[str]:
        return self.settings.themes

    def get_theme_variables(self, theme: str) -> Dict[str, Any]:
        return self.settings.get(THEME_VARIABLES.format(theme=theme), {})

    @property
    def output_style(self) -> Dict[str, Any]:
        return self.settings.output_style

    @property
    def minified(self) -> bool:
        return self.settings.minified

    @property
    def token(self) -> str:
        return self.settings.token

    def generate_variables(self, variables: Dict[str, Any]) -> Iterator[str]:
        for name, value in variables.items():
            yield VARIABLE.format(name=name, value=value)

    def get_bulma_imports(self) -> Iterator[str]:
        for path in self.bulma_path.iterdir():
            if path.is_dir():
                yield IMPORT.format(path=(path / ALL).relative_to(self.path).as_posix())

    def get_extension_imports(self) -> Iterator[str]:
        for extension in (self.path / EXTENSIONS).iterdir():
            if self.is_enabled_path(extension):
                for path in self.get_sass_files(extension):
                    yield IMPORT.format(path=path.as_posix())

    def get_required_js_files(self) -> Iterator[str]:
        for extension in (self.path / EXTENSIONS).iterdir():
            if self.is_enabled_path(extension):
                for path in self.get_js_files(extension):
                    yield path.as_posix()

    def include_css(self, css: str) -> str:
        return INCLUDE_CSS.format(css=css)

    def include_js(self, js: str) -> str:
        return INCLUDE_JS.format(js=js)

    def include_required(self) -> Iterator[str]:
        for required in self.get_required_js_files():
            yield self.include_js(required)

    def generate_theme(self, theme: Optional[str] = None) -> Iterator[str]:
        variables = self.variables.copy()

        if theme is not None:
            variables.update(self.get_theme_variables(theme))

        yield CHARSET
        yield EMPTY
        yield COMMENT_VARIABLE
        yield from self.generate_variables(variables)
        yield EMPTY
        yield from self.get_bulma_imports()
        yield EMPTY
        yield from self.get_extension_imports()
        yield EMPTY

    def generate_themes(self) -> Iterator[Iterator[str]]:
        yield self.generate_theme()

        for theme in self.themes:
            yield self.generate_theme(theme)

    def compile_theme(self, theme: Optional[str] = None) -> str:
        source = NEWLINE.join(self.generate_theme(theme))

        return sass.compile(
            string=source, output_style=self.output_style, include_paths=[self.path.as_posix()]
        )

    def compile_themes(self) -> Iterator[str]:
        yield self.compile_theme()

        for theme in self.themes:
            yield self.compile_theme(theme)

    def save_theme(
        self, theme: Optional[str] = None, root: Optional[Union[str, Path]] = None
    ) -> str:
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

        return path.relative_to(root).as_posix()

    def save_themes(
        self, root: Optional[Union[str, Path]] = None
    ) -> Iterator[str]:
        yield self.save_theme(root=root)

        for theme in self.themes:
            yield self.save_theme(theme, root=root)

    def compile_path(self, path: Union[str, Path]) -> str:
        return sass.compile(
            string=IMPORT.format(path=Path(path).as_posix(), output_style=self.output_style)
        )

    def compile_custom_css(self) -> Iterator[str]:
        for path in self.get_custom_files():
            yield self.compile_path(path)

    def save_custom_css(self, root: Optional[Union[str, Path]] = None) -> Iterator[str]:
        if root is None:
            root = self.path

        root = Path(root)

        for path in self.get_custom_files():
            output = self.compile_path(path)

            path = (root / CUSTOM / path).with_suffix(CSS_SUFFIX)

            path.parent.mkdir(exist_ok=True)

            path.write_text(output, encoding=UTF_8)

            yield path.relative_to(root).as_posix()

    def get_custom_files(self) -> Iterator[Path]:
        for path in self.custom:
            yield Path(path)

    def get_sass_files_impl(self, extension_path: Path) -> Iterator[Path]:
        for relative_path, pattern in SASS_PATTERNS:
            for path in (extension_path / relative_path).rglob(pattern):
                if pattern.endswith(CSS_SUFFIX):
                    path = path.with_suffix(EMPTY)

                if path.name == ALL or not is_private(path.name):
                    yield path.relative_to(self.path)

    def get_sass_files(self, extension_path: Path) -> Iterator[Path]:
        return unique(self.get_sass_files_impl(extension_path))

    def get_js_files(self, extension_path: Path) -> Iterator[Path]:
        path = extension_path / DIST

        files = (
            file.relative_to(self.path) for file in path.rglob(JS_PATTERN)
            if TEST_SUFFIX not in file.suffixes  # exclude test files
        )

        if self.minified:  # if we need to minify...
            minified_files = {
                minified_file.name: minified_file.relative_to(self.path)
                for minified_file in path.rglob(MIN_JS_PATTERN)
            }

            for file in files:  # ... go through normal files and yield minified versions, if found
                yield minified_files.get(file.name, file)

        else:
            yield from files
