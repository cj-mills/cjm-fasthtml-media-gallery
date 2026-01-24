"""Demo application for cjm-fasthtml-media-gallery library.

This demo showcases the media gallery component:

1. FileScanner Integration:
   - Recursive directory scanning for media files
   - File type detection and categorization
   - Caching for performance

2. DirectoryMounter:
   - Static file serving for media playback
   - Automatic URL generation for files

3. GalleryConfig:
   - View modes (grid, list)
   - Type filtering (audio, video, image, document)
   - Pagination support
   - Preview modal with playback

4. HTMX Integration:
   - Partial page updates for view/filter changes
   - Modal previews without page reload
   - Smooth navigation

Run with: python demo_app.py
"""

from pathlib import Path


def main():
    """Main entry point - initializes media gallery and starts the server."""
    from fasthtml.common import fast_app, Div, H1, H2, P, Span, A, Input, Label, APIRouter

    # DaisyUI and Tailwind utilities
    from cjm_fasthtml_daisyui.core.resources import get_daisyui_headers
    from cjm_fasthtml_daisyui.core.testing import create_theme_persistence_script
    from cjm_fasthtml_daisyui.components.actions.button import btn, btn_colors, btn_sizes
    from cjm_fasthtml_daisyui.components.data_display.badge import badge, badge_colors
    from cjm_fasthtml_daisyui.components.data_display.card import card, card_body
    from cjm_fasthtml_daisyui.utilities.semantic_colors import bg_dui, text_dui

    from cjm_fasthtml_tailwind.utilities.spacing import p, m
    from cjm_fasthtml_tailwind.utilities.sizing import container, max_w, w, h
    from cjm_fasthtml_tailwind.utilities.typography import font_size, font_weight, text_align
    from cjm_fasthtml_tailwind.utilities.flexbox_and_grid import (
        flex_display, flex_direction, items, justify, grid_display, grid_cols, gap
    )
    from cjm_fasthtml_tailwind.utilities.borders import border, rounded
    from cjm_fasthtml_tailwind.utilities.layout import overflow
    from cjm_fasthtml_tailwind.core.base import combine_classes

    # App core utilities
    from cjm_fasthtml_app_core.components.navbar import create_navbar
    from cjm_fasthtml_app_core.core.routing import register_routes
    from cjm_fasthtml_app_core.core.htmx import handle_htmx_request
    from cjm_fasthtml_app_core.core.layout import wrap_with_layout

    # File discovery
    from cjm_file_discovery.core.models import FileInfo, FileType
    from cjm_file_discovery.core.config import ScanConfig, FilterConfig as DiscoveryFilterConfig
    from cjm_file_discovery.scanning.scanner import FileScanner

    # Media gallery components
    from cjm_fasthtml_media_gallery.core.config import (
        GalleryConfig, FilterConfig, GridConfig, ListConfig,
        PaginationConfig, PreviewConfig, ViewMode, SelectionMode
    )
    from cjm_fasthtml_media_gallery.routes.handlers import GalleryState, init_router
    from cjm_fasthtml_media_gallery.components.gallery import render_media_gallery
    from cjm_fasthtml_media_gallery.serving.mounter import DirectoryMounter

    print("\n" + "=" * 70)
    print("Initializing cjm-fasthtml-media-gallery Demo")
    print("=" * 70)

    # Create the FastHTML app
    app, rt = fast_app(
        pico=False,
        hdrs=[
            *get_daisyui_headers(),
            create_theme_persistence_script(),
        ],
        title="Media Gallery Demo",
        htmlkw={'data-theme': 'light'},
        secret_key="demo-secret-key"
    )

    router = APIRouter(prefix="")

    print("  FastHTML app created successfully")

    # Default scan directory (home directory)
    # home_path = str(Path.home())
    home_path = "/mnt/SN850X_8TB/Media_Library/Images"

    # Demo directories to scan - you can customize these
    demo_directories = [home_path]

    # Create directory mounter for static file serving
    print("\n[1/4] Creating DirectoryMounter...")
    mounter = DirectoryMounter()
    print("  DirectoryMounter created")

    # Create scan configuration for media files
    print("\n[2/4] Creating file scanner configuration...")
    scan_config = ScanConfig(
        directories=demo_directories,
        recursive=True,
        max_depth=3,  # Limit depth for demo
        filter_config=DiscoveryFilterConfig(
            file_types=[FileType.AUDIO, FileType.VIDEO, FileType.IMAGE, FileType.DOCUMENT],
            include_hidden=False,
        ),
        cache_results=True,
        cache_duration_seconds=300,
        max_results=500,  # Limit results for demo
        sort_by="modified",
        sort_descending=True,
    )
    scanner = FileScanner(scan_config)
    print(f"  Configured to scan: {demo_directories}")
    print(f"  Max depth: {scan_config.max_depth}")
    print(f"  Max results: {scan_config.max_results}")

    # Create gallery configurations
    print("\n[3/4] Creating gallery configurations...")

    # Demo 1: Full media gallery (all media types)
    full_gallery_config = GalleryConfig(
        default_view=ViewMode.GRID,
        allow_view_toggle=True,
        grid=GridConfig(columns=4, show_thumbnails=True, show_file_size=True),
        list=ListConfig(show_icons=True, striped=True),
        filter=FilterConfig(
            enabled_types=[FileType.AUDIO, FileType.VIDEO, FileType.IMAGE, FileType.DOCUMENT],
            allow_type_filter=True,
        ),
        pagination=PaginationConfig(items_per_page=24, show_pagination=True),
        preview=PreviewConfig(enable_preview=True, show_navigation=True),
        selection_mode=SelectionMode.NONE,
        gallery_id="full-gallery",
        content_id="full-gallery-content",
        controls_id="full-gallery-controls",
        preview_modal_id="full-gallery-preview",
    )

    # Demo 2: Image-only gallery
    image_gallery_config = GalleryConfig(
        default_view=ViewMode.GRID,
        allow_view_toggle=True,
        grid=GridConfig(columns=5, show_thumbnails=True),
        filter=FilterConfig(
            enabled_types=[FileType.IMAGE],
            allow_type_filter=False,
        ),
        pagination=PaginationConfig(items_per_page=30),
        preview=PreviewConfig(enable_preview=True),
        selection_mode=SelectionMode.MULTIPLE,
        max_selections=10,
        gallery_id="image-gallery",
        content_id="image-gallery-content",
        controls_id="image-gallery-controls",
        preview_modal_id="image-gallery-preview",
    )

    # Demo 3: Audio/Video gallery
    av_gallery_config = GalleryConfig(
        default_view=ViewMode.LIST,
        allow_view_toggle=True,
        list=ListConfig(show_icons=True, compact=False),
        filter=FilterConfig(
            enabled_types=[FileType.AUDIO, FileType.VIDEO],
            allow_type_filter=True,
        ),
        pagination=PaginationConfig(items_per_page=20),
        preview=PreviewConfig(enable_preview=True, autoplay_video=False, autoplay_audio=False),
        selection_mode=SelectionMode.SINGLE,
        gallery_id="av-gallery",
        content_id="av-gallery-content",
        controls_id="av-gallery-controls",
        preview_modal_id="av-gallery-preview",
    )

    print("  Created 3 gallery configurations:")
    print("    - Full media gallery (all types, grid view)")
    print("    - Image gallery (images only, multi-select)")
    print("    - Audio/Video gallery (A/V only, list view)")

    # State management
    gallery_states = {
        "full": GalleryState(
            view_mode=ViewMode.GRID,
            active_types=[FileType.AUDIO, FileType.VIDEO, FileType.IMAGE, FileType.DOCUMENT]
        ),
        "image": GalleryState(
            view_mode=ViewMode.GRID,
            active_types=[FileType.IMAGE]
        ),
        "av": GalleryState(
            view_mode=ViewMode.LIST,
            active_types=[FileType.AUDIO, FileType.VIDEO]
        ),
    }

    # Track current scan directory for dynamic rescanning
    current_scan_path = {"path": home_path}

    def get_state(gallery_id: str):
        def getter():
            return gallery_states[gallery_id]
        return getter

    def set_state(gallery_id: str):
        def setter(state: GalleryState):
            gallery_states[gallery_id] = state
        return setter

    def get_files():
        """Get scanned files (uses cached results if valid)."""
        return scanner.scan()

    def get_type_counts(files):
        """Count files by type."""
        counts = {}
        for f in files:
            counts[f.file_type] = counts.get(f.file_type, 0) + 1
        return counts

    # Create routers for each gallery
    print("\n[4/4] Creating gallery routers...")

    full_gallery_router = init_router(
        config=full_gallery_config,
        files_getter=get_files,
        mounter=mounter,
        state_getter=get_state("full"),
        state_setter=set_state("full"),
        route_prefix="/gallery/full",
    )

    image_gallery_router = init_router(
        config=image_gallery_config,
        files_getter=get_files,
        mounter=mounter,
        state_getter=get_state("image"),
        state_setter=set_state("image"),
        route_prefix="/gallery/image",
    )

    av_gallery_router = init_router(
        config=av_gallery_config,
        files_getter=get_files,
        mounter=mounter,
        state_getter=get_state("av"),
        state_setter=set_state("av"),
        route_prefix="/gallery/av",
    )

    print("  Created 3 gallery routers")

    # Define page routes
    @router
    def index(request):
        """Homepage with demo overview."""

        def home_content():
            return Div(
                H1("Media Gallery Demo",
                   cls=combine_classes(font_size._4xl, font_weight.bold, m.b(4))),

                P("Display media file collections with type-specific previews and playback.",
                  cls=combine_classes(font_size.lg, text_dui.base_content, m.b(8))),

                # Feature cards
                Div(
                    # Full gallery card
                    Div(
                        Div(
                            H2("Full Media Gallery",
                               cls=combine_classes(font_size.xl, font_weight.semibold, m.b(2))),
                            P("Browse all media types with filtering and preview.",
                              cls=combine_classes(text_dui.base_content, m.b(4))),
                            Div(
                                Span("Grid view", cls=combine_classes(badge, badge_colors.primary, m.r(2))),
                                Span("All types", cls=combine_classes(badge, badge_colors.secondary, m.r(2))),
                                Span("Preview", cls=combine_classes(badge, badge_colors.accent)),
                                cls=m.b(4)
                            ),
                            A("Open Gallery →",
                              href=demo_full.to(),
                              cls=combine_classes(btn, btn_colors.primary)),
                            cls=card_body
                        ),
                        cls=combine_classes(card, bg_dui.base_200)
                    ),

                    # Image gallery card
                    Div(
                        Div(
                            H2("Image Gallery",
                               cls=combine_classes(font_size.xl, font_weight.semibold, m.b(2))),
                            P("Browse images with multi-select support.",
                              cls=combine_classes(text_dui.base_content, m.b(4))),
                            Div(
                                Span("Multi-select", cls=combine_classes(badge, badge_colors.primary, m.r(2))),
                                Span("Images only", cls=combine_classes(badge, badge_colors.success, m.r(2))),
                                Span("Thumbnails", cls=combine_classes(badge, badge_colors.info)),
                                cls=m.b(4)
                            ),
                            A("Open Gallery →",
                              href=demo_image.to(),
                              cls=combine_classes(btn, btn_colors.secondary)),
                            cls=card_body
                        ),
                        cls=combine_classes(card, bg_dui.base_200)
                    ),

                    # Audio/Video gallery card
                    Div(
                        Div(
                            H2("Audio/Video Gallery",
                               cls=combine_classes(font_size.xl, font_weight.semibold, m.b(2))),
                            P("Browse audio and video files with playback preview.",
                              cls=combine_classes(text_dui.base_content, m.b(4))),
                            Div(
                                Span("Single-select", cls=combine_classes(badge, badge_colors.primary, m.r(2))),
                                Span("List view", cls=combine_classes(badge, badge_colors.secondary, m.r(2))),
                                Span("Playback", cls=combine_classes(badge, badge_colors.warning)),
                                cls=m.b(4)
                            ),
                            A("Open Gallery →",
                              href=demo_av.to(),
                              cls=combine_classes(btn, btn_colors.accent)),
                            cls=card_body
                        ),
                        cls=combine_classes(card, bg_dui.base_200)
                    ),

                    cls=combine_classes(
                        grid_display, grid_cols(1),
                        grid_cols(3).md,
                        gap(6), m.b(8)
                    )
                ),

                # Info section
                Div(
                    H2("Features", cls=combine_classes(font_size._2xl, font_weight.bold, m.b(4))),
                    Div(
                        Div("✓ Grid and list view modes", cls=m.b(2)),
                        Div("✓ Type-based filtering (audio, video, image, document)", cls=m.b(2)),
                        Div("✓ Preview modal with media playback", cls=m.b(2)),
                        Div("✓ Pagination support", cls=m.b(2)),
                        Div("✓ Selection modes (none, single, multiple)", cls=m.b(2)),
                        Div("✓ Recursive directory scanning", cls=m.b(2)),
                        Div("✓ File caching for performance", cls=m.b(2)),
                        Div("✓ HTMX-powered partial updates", cls=m.b(2)),
                        cls=combine_classes(text_align.left, max_w.md, m.x.auto)
                    ),
                    cls=m.b(8)
                ),

                # Current scan info
                Div(
                    P(f"Currently scanning: {current_scan_path['path']}",
                      cls=combine_classes(font_size.sm, text_dui.base_content.opacity(70))),
                    cls=m.t(8)
                ),

                cls=combine_classes(
                    container,
                    max_w._6xl,
                    m.x.auto,
                    p(8),
                    text_align.center
                )
            )

        return handle_htmx_request(
            request,
            home_content,
            wrap_fn=lambda content: wrap_with_layout(content, navbar=navbar)
        )

    @router
    def demo_full(request):
        """Full media gallery demo."""

        def gallery_content():
            # Mount directories for this demo
            mounter.mount(app, scanner.config.directories)

            files = get_files()
            state = gallery_states["full"]
            type_counts = get_type_counts(files)

            return Div(
                # Header
                Div(
                    H1("Full Media Gallery",
                       cls=combine_classes(font_size._2xl, font_weight.bold)),
                    P(f"Showing {len(files)} media files from {current_scan_path['path']}",
                      cls=combine_classes(text_dui.base_content, font_size.sm)),
                    cls=combine_classes(m.b(4))
                ),

                # Gallery
                Div(
                    render_media_gallery(
                        files=files,
                        config=full_gallery_config,
                        view_mode=state.view_mode,
                        active_types=state.active_types,
                        get_file_url=mounter.get_url,
                        selected_paths=state.selected_paths,
                        toggle_view_url=full_gallery_router.toggle_view.to(),
                        filter_url=full_gallery_router.filter_type.to(),
                        preview_url=full_gallery_router.preview.to(),
                        page_url=full_gallery_router.page.to(),
                        current_page=state.current_page,
                        total_items=len(files),
                        type_counts=type_counts,
                    ),
                    cls=combine_classes(h("screen-3/4"), border(), rounded.lg, overflow.hidden)
                ),

                cls=combine_classes(container, max_w._6xl, m.x.auto, p(6))
            )

        return handle_htmx_request(
            request,
            gallery_content,
            wrap_fn=lambda content: wrap_with_layout(content, navbar=navbar)
        )

    @router
    def demo_image(request):
        """Image gallery demo."""

        def gallery_content():
            # Mount directories for this demo
            mounter.mount(app, scanner.config.directories)

            files = get_files()
            # Filter to images only for count
            image_files = [f for f in files if f.file_type == FileType.IMAGE]
            state = gallery_states["image"]

            return Div(
                # Header
                Div(
                    H1("Image Gallery",
                       cls=combine_classes(font_size._2xl, font_weight.bold)),
                    P(f"Showing {len(image_files)} images. Multi-select enabled (max 10).",
                      cls=combine_classes(text_dui.base_content, font_size.sm)),
                    cls=combine_classes(m.b(4))
                ),

                # Selection display
                Div(
                    Span("Selected: ", cls=font_weight.semibold),
                    Span(
                        f"{len(state.selected_paths)} images" if state.selected_paths else "None",
                        cls=text_dui.base_content
                    ),
                    cls=combine_classes(m.b(4), p(2), bg_dui.base_200, rounded())
                ),

                # Gallery
                Div(
                    render_media_gallery(
                        files=image_files,
                        config=image_gallery_config,
                        view_mode=state.view_mode,
                        active_types=state.active_types,
                        get_file_url=mounter.get_url,
                        selected_paths=state.selected_paths,
                        toggle_view_url=image_gallery_router.toggle_view.to(),
                        preview_url=image_gallery_router.preview.to(),
                        select_url=image_gallery_router.select.to(),
                        page_url=image_gallery_router.page.to(),
                        current_page=state.current_page,
                        total_items=len(image_files),
                    ),
                    cls=combine_classes(h("screen-3/4"), border(), rounded.lg, overflow.hidden)
                ),

                cls=combine_classes(container, max_w._6xl, m.x.auto, p(6))
            )

        return handle_htmx_request(
            request,
            gallery_content,
            wrap_fn=lambda content: wrap_with_layout(content, navbar=navbar)
        )

    @router
    def demo_av(request):
        """Audio/Video gallery demo."""

        def gallery_content():
            # Mount directories for this demo
            mounter.mount(app, scanner.config.directories)

            files = get_files()
            # Filter to audio/video only
            av_files = [f for f in files if f.file_type in [FileType.AUDIO, FileType.VIDEO]]
            state = gallery_states["av"]
            type_counts = get_type_counts(av_files)

            return Div(
                # Header
                Div(
                    H1("Audio/Video Gallery",
                       cls=combine_classes(font_size._2xl, font_weight.bold)),
                    P(f"Showing {len(av_files)} audio/video files. Single selection mode.",
                      cls=combine_classes(text_dui.base_content, font_size.sm)),
                    cls=combine_classes(m.b(4))
                ),

                # Selection display
                Div(
                    Span("Selected: ", cls=font_weight.semibold),
                    Span(
                        Path(state.selected_paths[0]).name if state.selected_paths else "None",
                        cls=text_dui.base_content
                    ),
                    cls=combine_classes(m.b(4), p(2), bg_dui.base_200, rounded())
                ),

                # Gallery
                Div(
                    render_media_gallery(
                        files=av_files,
                        config=av_gallery_config,
                        view_mode=state.view_mode,
                        active_types=state.active_types,
                        get_file_url=mounter.get_url,
                        selected_paths=state.selected_paths,
                        toggle_view_url=av_gallery_router.toggle_view.to(),
                        filter_url=av_gallery_router.filter_type.to(),
                        preview_url=av_gallery_router.preview.to(),
                        select_url=av_gallery_router.select.to(),
                        page_url=av_gallery_router.page.to(),
                        current_page=state.current_page,
                        total_items=len(av_files),
                        type_counts=type_counts,
                    ),
                    cls=combine_classes(h("screen-3/4"), border(), rounded.lg, overflow.hidden)
                ),

                cls=combine_classes(container, max_w._6xl, m.x.auto, p(6))
            )

        return handle_htmx_request(
            request,
            gallery_content,
            wrap_fn=lambda content: wrap_with_layout(content, navbar=navbar)
        )

    # Create navbar
    navbar = create_navbar(
        title="Media Gallery Demo",
        nav_items=[
            ("Home", index),
            ("Full Gallery", demo_full),
            ("Images", demo_image),
            ("Audio/Video", demo_av),
        ],
        home_route=index,
        theme_selector=True
    )

    # Register all routes
    register_routes(
        app,
        router,
        full_gallery_router,
        image_gallery_router,
        av_gallery_router,
    )

    # Initial scan
    print("\n" + "=" * 70)
    print("Performing initial file scan...")
    print("=" * 70)
    files = scanner.scan()
    summary = scanner.get_summary()
    print(f"  Total files: {summary['total_files']}")
    print(f"  Total size: {summary['total_size_str']}")
    print(f"  By type: {summary['by_type']}")

    # Debug: Print registered routes
    print("\n" + "=" * 70)
    print("Registered Routes:")
    print("=" * 70)
    for route in app.routes:
        if hasattr(route, 'path'):
            print(f"  {route.path}")

    print("\n" + "=" * 70)
    print("Demo App Ready!")
    print("=" * 70)
    print("\n Library Components:")
    print("  - FileScanner - Recursive media file discovery")
    print("  - DirectoryMounter - Static file serving")
    print("  - GalleryConfig - Configurable gallery settings")
    print("  - GalleryState - View/filter/selection state tracking")
    print("  - render_media_gallery - Main UI component")
    print("  - HTMX handlers - Smooth partial page updates")
    print("=" * 70 + "\n")

    return app


if __name__ == "__main__":
    import uvicorn
    import webbrowser
    import threading

    # Call main to initialize everything and get the app
    app = main()

    def open_browser(url):
        print(f"Opening browser at {url}")
        webbrowser.open(url)

    port = 5033
    host = "0.0.0.0"
    display_host = 'localhost' if host in ['0.0.0.0', '127.0.0.1'] else host

    print(f"Server: http://{display_host}:{port}")
    print("\nAvailable routes:")
    print(f"  http://{display_host}:{port}/              - Homepage with demo overview")
    print(f"  http://{display_host}:{port}/demo_full    - Full media gallery")
    print(f"  http://{display_host}:{port}/demo_image   - Image gallery (multi-select)")
    print(f"  http://{display_host}:{port}/demo_av      - Audio/Video gallery")
    print("\n" + "=" * 70 + "\n")

    # Open browser after a short delay
    timer = threading.Timer(1.5, lambda: open_browser(f"http://localhost:{port}"))
    timer.daemon = True
    timer.start()

    # Start server
    uvicorn.run(app, host=host, port=port)
