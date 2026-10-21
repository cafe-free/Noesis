"""
Central Textual stylesheet for Noesis TUI with teal, emerald, amber, and slate styling.
"""

APP_CSS = """
Screen {
    background: #0f172a;
    color: #f8fafc;
}

Header {
    dock: top;
    height: 3;
    background: #1e293b;
    color: #14b8a6;
    text-style: bold;
    border-bottom: hkey #0d9488;
}

Footer {
    dock: bottom;
    height: 1;
    background: #1e293b;
    color: #94a3b8;
}

/* Card Container */
.card {
    background: #1e293b;
    border: solid #334155;
    border-title-color: #14b8a6;
    border-title-style: bold;
    padding: 1 2;
    margin: 1 0;
}

.card:focus-within {
    border: solid #0d9488;
}

/* Button Variants */
Button {
    min-width: 14;
    height: 3;
    background: #334155;
    color: #f8fafc;
    border: none;
    text-style: bold;
}

Button:hover {
    background: #475569;
}

Button.-primary {
    background: #0d9488;
    color: #ffffff;
}

Button.-primary:hover {
    background: #14b8a6;
}

Button.-success {
    background: #10b981;
    color: #ffffff;
}

Button.-success:hover {
    background: #34d399;
}

Button.-danger {
    background: #e11d48;
    color: #ffffff;
}

Button.-danger:hover {
    background: #f43f5e;
}

Button.-ghost {
    background: transparent;
    color: #94a3b8;
    border: solid #334155;
}

Button.-ghost:hover {
    background: #334155;
    color: #f8fafc;
}

/* Inputs */
Input {
    background: #0f172a;
    border: solid #334155;
    color: #f8fafc;
    padding: 0 1;
}

Input:focus {
    border: solid #14b8a6;
}

/* Data Tables */
DataTable {
    background: #0f172a;
    border: solid #334155;
    height: auto;
    max-height: 16;
}

DataTable > .datatable--header {
    background: #1e293b;
    color: #14b8a6;
    text-style: bold;
}

DataTable > .datatable--cursor {
    background: #0d9488;
    color: #ffffff;
    text-style: bold;
}

/* Stat Widgets */
.stat-box {
    background: #1e293b;
    border: solid #334155;
    padding: 1 2;
    margin: 0 1;
    height: auto;
}

.stat-label {
    color: #94a3b8;
    text-style: bold;
}

.stat-value {
    color: #14b8a6;
    text-style: bold;
    text-align: center;
}

/* Quiz Specific */
.choice-btn {
    width: 100%;
    margin: 1 0;
    text-align: left;
    background: #1e293b;
    border: solid #334155;
    color: #f8fafc;
}

.choice-btn:focus {
    border: solid #14b8a6;
    background: #0d9488;
    color: #ffffff;
}

.word-chip {
    margin: 0 1;
    background: #334155;
    color: #f8fafc;
}

.word-chip:hover {
    background: #0d9488;
}

/* Badges and Feedback */
.feedback-correct {
    background: #064e3b;
    color: #a7f3d0;
    border: solid #10b981;
    padding: 1 2;
    margin: 1 0;
}

.feedback-incorrect {
    background: #4c0519;
    color: #fecdd3;
    border: solid #f43f5e;
    padding: 1 2;
    margin: 1 0;
}

/* Dialog / Modal Screens */
ModalScreen {
    align: center middle;
    background: rgba(15, 23, 42, 0.75);
}

.modal-dialog {
    width: 65;
    max-width: 90%;
    height: auto;
    background: #1e293b;
    border: solid #0d9488;
    padding: 1 2;
}
"""
