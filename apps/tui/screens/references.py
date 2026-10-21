from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import BindingType
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Header, Input, Label, Static


class ReferencesScreen(Screen):
    """RAG Private Knowledge Base manager and Semantic Search tester."""

    BINDINGS: ClassVar[list[BindingType]] = [
        ("escape", "back_dashboard", "Back to Dashboard"),
        ("s", "focus_search", "Search"),
    ]

    def __init__(self):
        super().__init__()
        self.references: list[dict] = []

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Container(classes="card"):
            yield Static("📚 [bold teal]Private Knowledge Base (RAG)[/bold teal]")
            yield Static(
                "Add reference materials from websites or documents for semantic retrieval.",
                classes="stat-label",
            )

            # Search Section
            with Vertical(id="rag-search-box"):
                yield Label("Semantic RAG Search across your knowledge base:")
                with Horizontal():
                    yield Input(placeholder="e.g., What are Spanish reflexive verbs?", id="input-rag-search")
                    yield Button("Search", variant="primary", id="btn-rag-search", classes="-primary")
                yield Static("", id="lbl-search-results", classes="stat-label")

        # Ingestion Actions
        with Container(classes="card"):
            yield Static("Add Reference Material", classes="stat-label")
            with Horizontal():
                with Vertical(classes="stat-box"):
                    yield Label("Add Website / URL:")
                    yield Input(placeholder="https://example.com/article", id="input-web-url")
                    yield Button("Add Website", id="btn-add-url", classes="-primary")

                with Vertical(classes="stat-box"):
                    yield Label("Upload Document (PDF, TXT, MD path):")
                    yield Input(placeholder="/path/to/grammar_notes.pdf", id="input-doc-path")
                    yield Button("Upload Document", id="btn-upload-doc", classes="-success")

        # Source List Table
        with Container(classes="card"):
            yield Static("Your Reference Sources", classes="stat-label")
            yield DataTable(id="table-references", cursor_type="row")
            with Horizontal():
                yield Button("Delete Selected Reference", id="btn-del-ref", classes="-danger")
                yield Button("Back to Dashboard", variant="default", id="btn-back-dash", classes="-ghost")

    async def on_mount(self) -> None:
        table = self.query_one("#table-references", DataTable)
        table.add_columns("#", "Title", "Type", "Chunks", "Status", "Source")
        await self.load_references()

    async def load_references(self) -> None:
        client = self.app.client
        self.references = await client.list_references()
        table = self.query_one("#table-references", DataTable)
        table.clear()

        if not self.references:
            table.add_row("-", "No references indexed yet.", "-", "0", "-", "-")
        else:
            for i, r in enumerate(self.references):
                src = r.get("source_url") or r.get("file_name") or "-"
                table.add_row(
                    str(i + 1),
                    r.get("title", "Untitled Reference"),
                    r.get("source_type", "txt").upper(),
                    str(r.get("chunk_count", 0)),
                    r.get("status", "ready").capitalize(),
                    str(src)[:35],
                    key=str(r.get("id")),
                )

    def action_focus_search(self) -> None:
        self.query_one("#input-rag-search", Input).focus()

    def action_back_dashboard(self) -> None:
        self.app.switch_screen("dashboard")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-rag-search":
            self.run_worker(self.perform_search())
        elif event.button.id == "btn-add-url":
            self.run_worker(self.add_url())
        elif event.button.id == "btn-upload-doc":
            self.run_worker(self.upload_doc())
        elif event.button.id == "btn-del-ref":
            self.run_worker(self.delete_selected())
        elif event.button.id == "btn-back-dash":
            self.action_back_dashboard()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "input-rag-search":
            self.run_worker(self.perform_search())
        elif event.input.id == "input-web-url":
            self.run_worker(self.add_url())
        elif event.input.id == "input-doc-path":
            self.run_worker(self.upload_doc())

    async def perform_search(self) -> None:
        q = self.query_one("#input-rag-search", Input).value.strip()
        if not q:
            return

        res_lbl = self.query_one("#lbl-search-results", Static)
        res_lbl.update("[dim]Searching vector embeddings...[/dim]")

        try:
            results = await self.app.client.search_references(query=q, top_k=3)
            if not results:
                res_lbl.update("[yellow]No relevant chunks matched the query.[/yellow]")
                return

            lines = [f"[bold green]Found {len(results)} relevant knowledge chunks:[/bold green]"]
            for r in results:
                title = r.get("document_title", "Reference")
                sim = int(r.get("similarity", 0) * 100)
                snippet = r.get("content", "").replace("\n", " ")[:120]
                lines.append(f"• [bold]{title}[/bold] ({sim}% Match): \"{snippet}...\"")

            res_lbl.update("\n".join(lines))
        except Exception as e:
            res_lbl.update(f"[bold red]Search error: {e}[/bold red]")

    async def add_url(self) -> None:
        inp = self.query_one("#input-web-url", Input)
        url = inp.value.strip()
        if not url:
            self.app.notify("Please enter a website URL.", severity="warning")
            return

        self.app.notify("Ingesting website...", severity="information")
        try:
            await self.app.client.add_url_reference(url=url)
            inp.value = ""
            self.app.notify("Website added and indexed!", severity="information")
            await self.load_references()
        except Exception as e:
            self.app.notify(f"Failed to add URL: {e}", severity="error")

    async def upload_doc(self) -> None:
        inp = self.query_one("#input-doc-path", Input)
        path = inp.value.strip()
        if not path:
            self.app.notify("Please enter a document file path.", severity="warning")
            return

        self.app.notify("Uploading and indexing document...", severity="information")
        try:
            await self.app.client.upload_file_reference(file_path=path)
            inp.value = ""
            self.app.notify("Document indexed successfully!", severity="information")
            await self.load_references()
        except Exception as e:
            self.app.notify(f"Failed to upload document: {e}", severity="error")

    async def delete_selected(self) -> None:
        table = self.query_one("#table-references", DataTable)
        if table.row_count == 0 or not self.references:
            return

        cursor_row = table.cursor_row
        if 0 <= cursor_row < len(self.references):
            doc = self.references[cursor_row]
            doc_id = str(doc.get("id"))
            try:
                await self.app.client.delete_reference(doc_id)
                self.app.notify("Reference deleted.", severity="information")
                await self.load_references()
            except Exception as e:
                self.app.notify(f"Could not delete reference: {e}", severity="error")
