"""JS/CSS Webpack bundles for InvenioRDM Starter."""

from invenio_assets.webpack import WebpackThemeBundle

theme = WebpackThemeBundle(
    __name__,
    "assets",
    default="semantic-ui",
    themes={
        "semantic-ui": dict(
            entry={
                # Inter font definitions
                "invenio-rdm-starter-fonts": "./less/invenio_rdm_starter/fonts.less",
            },
        ),
    },
)
