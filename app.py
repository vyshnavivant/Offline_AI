import customtkinter as ctk
import ollama
import threading
import json
import os
import uuid
from datetime import datetime

# ============================================================
# SETTINGS
# ============================================================

MODEL_NAME = "llama3"
CHAT_FILE = "chats.json"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ============================================================
# COLORS
# ============================================================

BG = "#212121"
SIDEBAR = "#171717"
CARD = "#2A2A2A"
USER_BUBBLE = "#343541"
INPUT = "#303030"
TEXT = "#ECECEC"
SECONDARY = "#9B9B9B"
BORDER = "#3A3A3A"
ACCENT = "#10A37F"
HOVER = "#2F2F2F"

# ============================================================
# APP
# ============================================================

app = ctk.CTk()
app.title("Offline AI")
app.geometry("1200x760")
app.minsize(900, 600)

# ============================================================
# DATA
# ============================================================

chats = {}
current_chat_id = None


# ============================================================
# LOAD / SAVE
# ============================================================

def load_chats():

    global chats

    if os.path.exists(CHAT_FILE):

        try:

            with open(
                CHAT_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                chats = json.load(file)

        except Exception:

            chats = {}

    else:

        chats = {}


def save_chats():

    try:

        with open(
            CHAT_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                chats,
                file,
                indent=4,
                ensure_ascii=False
            )

    except Exception as error:

        print(error)


# ============================================================
# SIDEBAR
# ============================================================

sidebar = ctk.CTkFrame(
    app,
    width=270,
    corner_radius=0,
    fg_color=SIDEBAR
)

sidebar.pack(
    side="left",
    fill="y"
)

sidebar.pack_propagate(False)


# Brand

brand = ctk.CTkFrame(
    sidebar,
    fg_color="transparent"
)

brand.pack(
    fill="x",
    padx=18,
    pady=(22, 18)
)


brand_icon = ctk.CTkLabel(
    brand,
    text="✦",
    font=ctk.CTkFont(size=26),
    text_color=ACCENT
)

brand_icon.pack(
    side="left",
    padx=(0, 10)
)


brand_text = ctk.CTkLabel(
    brand,
    text="Offline AI",
    font=ctk.CTkFont(
        size=21,
        weight="bold"
    )
)

brand_text.pack(
    side="left"
)


# New chat

new_chat_button = ctk.CTkButton(
    sidebar,
    text="＋  New chat",
    height=44,
    corner_radius=8,
    fg_color="transparent",
    border_width=1,
    border_color=BORDER,
    hover_color=HOVER,
    anchor="w",
    font=ctk.CTkFont(size=14),
    command=lambda: new_chat()
)

new_chat_button.pack(
    fill="x",
    padx=15,
    pady=(0, 20)
)


# Chat label

chat_label = ctk.CTkLabel(
    sidebar,
    text="RECENT CHATS",
    text_color=SECONDARY,
    anchor="w",
    font=ctk.CTkFont(
        size=11,
        weight="bold"
    )
)

chat_label.pack(
    fill="x",
    padx=20,
    pady=(0, 8)
)


# Chat list

history_frame = ctk.CTkScrollableFrame(
    sidebar,
    fg_color="transparent",
    scrollbar_button_color="#333333",
    scrollbar_button_hover_color="#444444"
)

history_frame.pack(
    fill="both",
    expand=True,
    padx=8
)


# Bottom area

bottom_frame = ctk.CTkFrame(
    sidebar,
    fg_color="transparent"
)

bottom_frame.pack(
    fill="x",
    padx=15,
    pady=15
)


local_indicator = ctk.CTkLabel(
    bottom_frame,
    text="●  Local AI",
    text_color=ACCENT,
    anchor="w",
    font=ctk.CTkFont(size=12)
)

local_indicator.pack(
    anchor="w"
)


local_model = ctk.CTkLabel(
    bottom_frame,
    text="Llama 3 • Offline",
    text_color=SECONDARY,
    anchor="w",
    font=ctk.CTkFont(size=11)
)

local_model.pack(
    anchor="w",
    pady=(2, 0)
)


# ============================================================
# MAIN
# ============================================================

main = ctk.CTkFrame(
    app,
    corner_radius=0,
    fg_color=BG
)

main.pack(
    side="right",
    fill="both",
    expand=True
)


# ============================================================
# HEADER
# ============================================================

header = ctk.CTkFrame(
    main,
    height=64,
    corner_radius=0,
    fg_color=BG
)

header.pack(
    fill="x"
)


header_title = ctk.CTkLabel(
    header,
    text="Offline AI",
    font=ctk.CTkFont(
        size=17,
        weight="bold"
    )
)

header_title.pack(
    side="left",
    padx=25
)


connection = ctk.CTkLabel(
    header,
    text="● Connected locally",
    text_color=ACCENT,
    font=ctk.CTkFont(size=12)
)

connection.pack(
    side="right",
    padx=25
)


# ============================================================
# CHAT AREA
# ============================================================

chat_area = ctk.CTkScrollableFrame(
    main,
    fg_color=BG,
    scrollbar_button_color="#3A3A3A",
    scrollbar_button_hover_color="#4A4A4A"
)

chat_area.pack(
    fill="both",
    expand=True,
    padx=50
)


# ============================================================
# WELCOME
# ============================================================

def show_welcome():

    for widget in chat_area.winfo_children():

        widget.destroy()

    welcome = ctk.CTkFrame(
        chat_area,
        fg_color="transparent"
    )

    welcome.pack(
        pady=130
    )


    icon = ctk.CTkLabel(
        welcome,
        text="✦",
        text_color=ACCENT,
        font=ctk.CTkFont(size=42)
    )

    icon.pack()


    title = ctk.CTkLabel(
        welcome,
        text="How can I help you?",
        font=ctk.CTkFont(
            size=30,
            weight="bold"
        )
    )

    title.pack(
        pady=(8, 5)
    )


    subtitle = ctk.CTkLabel(
        welcome,
        text="Ask anything. Your conversations stay on this computer.",
        text_color=SECONDARY,
        font=ctk.CTkFont(size=14)
    )

    subtitle.pack()


# ============================================================
# COPY TEXT
# ============================================================

def copy_text(text):

    app.clipboard_clear()
    app.clipboard_append(text)


# ============================================================
# MESSAGE
# ============================================================

def add_message(sender, message):

    if sender == "You":

        bubble_color = USER_BUBBLE

    else:

        bubble_color = CARD

    outer = ctk.CTkFrame(
        chat_area,
        fg_color="transparent"
    )

    outer.pack(
        fill="x",
        pady=9
    )


    bubble = ctk.CTkFrame(
        outer,
        fg_color=bubble_color,
        corner_radius=14
    )

    bubble.pack(
        fill="x",
        padx=20
    )


    top = ctk.CTkFrame(
        bubble,
        fg_color="transparent"
    )

    top.pack(
        fill="x",
        padx=15,
        pady=(12, 3)
    )


    if sender == "AI":

        icon_text = "✦"

        icon_color = ACCENT

    else:

        icon_text = "You"

        icon_color = TEXT


    sender_label = ctk.CTkLabel(
        top,
        text=icon_text,
        text_color=icon_color,
        font=ctk.CTkFont(
            size=13,
            weight="bold"
        )
    )

    sender_label.pack(
        side="left"
    )


    if sender == "AI":

        copy_button = ctk.CTkButton(
            top,
            text="Copy",
            width=55,
            height=25,
            corner_radius=6,
            fg_color="transparent",
            hover_color=HOVER,
            text_color=SECONDARY,
            font=ctk.CTkFont(size=11),
            command=lambda t=message: copy_text(t)
        )

        copy_button.pack(
            side="right"
        )


    message_label = ctk.CTkLabel(
        bubble,
        text=message,
        text_color=TEXT,
        justify="left",
        anchor="w",
        wraplength=760,
        font=ctk.CTkFont(
            size=14
        )
    )

    message_label.pack(
        fill="x",
        padx=15,
        pady=(3, 15)
    )


    chat_area.update_idletasks()

    chat_area._parent_canvas.yview_moveto(1)


# ============================================================
# INPUT
# ============================================================

input_wrapper = ctk.CTkFrame(
    main,
    fg_color=BG
)

input_wrapper.pack(
    fill="x",
    padx=50,
    pady=(5, 22)
)


input_box = ctk.CTkFrame(
    input_wrapper,
    height=58,
    corner_radius=15,
    fg_color=INPUT,
    border_width=1,
    border_color=BORDER
)

input_box.pack(
    fill="x"
)


message_entry = ctk.CTkEntry(
    input_box,
    placeholder_text="Message Offline AI...",
    height=52,
    border_width=0,
    fg_color="transparent",
    font=ctk.CTkFont(size=14)
)

message_entry.pack(
    side="left",
    fill="x",
    expand=True,
    padx=(15, 5)
)


send_button = ctk.CTkButton(
    input_box,
    text="↑",
    width=42,
    height=42,
    corner_radius=12,
    fg_color=ACCENT,
    hover_color="#0D8F70",
    font=ctk.CTkFont(
        size=21,
        weight="bold"
    ),
    command=lambda: send_message()
)

send_button.pack(
    side="right",
    padx=7
)


input_hint = ctk.CTkLabel(
    input_wrapper,
    text="Llama 3 runs locally through Ollama • No internet required",
    text_color="#777777",
    font=ctk.CTkFont(size=10)
)

input_hint.pack(
    pady=(6, 0)
)


# ============================================================
# SIDEBAR UPDATE
# ============================================================

def update_sidebar():

    for widget in history_frame.winfo_children():

        widget.destroy()

    sorted_chats = sorted(
        chats.values(),
        key=lambda x: x.get(
            "updated",
            ""
        ),
        reverse=True
    )

    for chat in sorted_chats:

        chat_id = chat["id"]

        row = ctk.CTkFrame(
            history_frame,
            fg_color="transparent"
        )

        row.pack(
            fill="x",
            pady=2
        )


        active = (
            chat_id == current_chat_id
        )


        button = ctk.CTkButton(
            row,
            text="  " + chat["title"],
            anchor="w",
            height=38,
            corner_radius=7,
            fg_color=(
                "#303030"
                if active
                else "transparent"
            ),
            hover_color=HOVER,
            text_color=TEXT,
            font=ctk.CTkFont(size=12),
            command=lambda cid=chat_id:
            open_chat(cid)
        )

        button.pack(
            side="left",
            fill="x",
            expand=True
        )


        delete = ctk.CTkButton(
            row,
            text="×",
            width=28,
            height=38,
            corner_radius=7,
            fg_color="transparent",
            hover_color="#552222",
            text_color=SECONDARY,
            command=lambda cid=chat_id:
            delete_chat(cid)
        )

        delete.pack(
            side="right"
        )


# ============================================================
# NEW CHAT
# ============================================================

def new_chat():

    global current_chat_id

    current_chat_id = None

    show_welcome()

    header_title.configure(
        text="New chat"
    )

    message_entry.delete(
        0,
        "end"
    )

    update_sidebar()

    message_entry.focus()


# ============================================================
# OPEN CHAT
# ============================================================

def open_chat(chat_id):

    global current_chat_id

    if chat_id not in chats:

        return

    current_chat_id = chat_id

    header_title.configure(
        text=chats[chat_id]["title"]
    )

    for widget in chat_area.winfo_children():

        widget.destroy()

    for msg in chats[chat_id]["messages"]:

        if msg["role"] == "user":

            add_message(
                "You",
                msg["content"]
            )

        elif msg["role"] == "assistant":

            add_message(
                "AI",
                msg["content"]
            )

    update_sidebar()


# ============================================================
# DELETE CHAT
# ============================================================

def delete_chat(chat_id):

    global current_chat_id

    if chat_id in chats:

        del chats[chat_id]

    save_chats()

    if current_chat_id == chat_id:

        current_chat_id = None

        header_title.configure(
            text="Offline AI"
        )

        show_welcome()

    update_sidebar()


# ============================================================
# CREATE CHAT
# ============================================================

def create_chat(question):

    global current_chat_id

    chat_id = str(
        uuid.uuid4()
    )

    title = question.strip()

    if len(title) > 35:

        title = title[:35] + "..."

    chats[chat_id] = {

        "id": chat_id,

        "title": title,

        "created": datetime.now().isoformat(),

        "updated": datetime.now().isoformat(),

        "messages": []

    }

    current_chat_id = chat_id

    return chat_id


# ============================================================
# OLLAMA
# ============================================================

def ask_ollama(chat_id):

    try:

        messages = chats[chat_id]["messages"]

        response = ollama.chat(
            model=MODEL_NAME,
            messages=messages
        )

        answer = response[
            "message"
        ]["content"]


        chats[chat_id][
            "messages"
        ].append(
            {
                "role": "assistant",
                "content": answer
            }
        )


        chats[chat_id][
            "updated"
        ] = datetime.now().isoformat()


        save_chats()


        app.after(
            0,
            lambda: add_message(
                "AI",
                answer
            )
        )


        app.after(
            0,
            update_sidebar
        )


        app.after(
            0,
            lambda: connection.configure(
                text="● Connected locally",
                text_color=ACCENT
            )
        )


    except Exception as error:

        app.after(
            0,
            lambda: add_message(
                "AI",
                "I couldn't connect to Ollama.\n\n"
                + str(error)
            )
        )


        app.after(
            0,
            lambda: connection.configure(
                text="● Connection error",
                text_color="#FF5555"
            )
        )


    finally:

        app.after(
            0,
            lambda: send_button.configure(
                state="normal"
            )
        )


# ============================================================
# SEND
# ============================================================

def send_message():

    global current_chat_id

    question = message_entry.get().strip()

    if not question:

        return


    message_entry.delete(
        0,
        "end"
    )


    if current_chat_id is None:

        current_chat_id = create_chat(
            question
        )

        for widget in chat_area.winfo_children():

            widget.destroy()

        header_title.configure(
            text=chats[current_chat_id][
                "title"
            ]
        )


    chats[current_chat_id][
        "messages"
    ].append(
        {
            "role": "user",
            "content": question
        }
    )


    chats[current_chat_id][
        "updated"
    ] = datetime.now().isoformat()


    save_chats()


    add_message(
        "You",
        question
    )


    update_sidebar()


    send_button.configure(
        state="disabled"
    )


    connection.configure(
        text="● Thinking...",
        text_color="#FFA500"
    )


    threading.Thread(
        target=ask_ollama,
        args=(current_chat_id,),
        daemon=True
    ).start()


# ============================================================
# ENTER
# ============================================================

message_entry.bind(
    "<Return>",
    lambda event: send_message()
)


# ============================================================
# START
# ============================================================

load_chats()

if chats:

    latest = sorted(
        chats.values(),
        key=lambda x: x.get(
            "updated",
            ""
        ),
        reverse=True
    )[0]

    open_chat(
        latest["id"]
    )

else:

    show_welcome()


message_entry.focus()

app.mainloop()