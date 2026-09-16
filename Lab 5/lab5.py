#!/usr/bin/env python3
"""Arabic GUI for AES-OFB PDF/file encryption and decryption."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes


KEY_SIZE = 16  # 16 bytes means AES-128.
IV_SIZE = AES.block_size  # AES uses a 16-byte block and IV size.
KEY_FILE_NAME = "aes_key.bin"  # The secret key is stored next to this program.


def key_file_path() -> Path:
    """Return the path of the key file beside this Python program."""
    return Path(__file__).resolve().parent / KEY_FILE_NAME


def get_or_create_key() -> bytes:
    """Load the existing AES key or create it once if it does not exist."""
    path = key_file_path()
    if path.exists():
        key = path.read_bytes()  # Reuse the same key so decryption remains possible.
        if len(key) != KEY_SIZE:
            raise ValueError("The key file must contain exactly 16 bytes.")
        return key

    key = get_random_bytes(KEY_SIZE)  # Generate a cryptographically secure AES-128 key.
    path.write_bytes(key)  # Save the key beside the program for future decryption.
    return key


def encrypt_file(input_path: Path) -> Path:
    """Encrypt the selected file and store IV before ciphertext."""
    key = get_or_create_key()  # Load or generate the key used for this operation.
    iv = get_random_bytes(IV_SIZE)  # Generate a fresh IV for this encryption operation.
    cipher = AES.new(key, AES.MODE_OFB, iv=iv)  # Create AES in OFB mode.
    plaintext = input_path.read_bytes()  # Read PDF bytes without treating them as text.
    ciphertext = cipher.encrypt(plaintext)  # OFB does not require padding.
    output_path = input_path.with_name(f"EN-{input_path.name}.aes")
    output_path.write_bytes(iv + ciphertext)  # Save IV first so decryption can recover it.
    return output_path


def decrypt_file(input_path: Path) -> Path:
    """Decrypt a file whose first 16 bytes contain the IV."""
    key = get_or_create_key()  # Load the same key that was used during encryption.
    encrypted_data = input_path.read_bytes()  # Read IV and ciphertext from the encrypted file.
    if len(encrypted_data) < IV_SIZE:
        raise ValueError("The encrypted file does not contain a valid IV.")

    iv = encrypted_data[:IV_SIZE]  # Extract the IV stored at the beginning of the file.
    ciphertext = encrypted_data[IV_SIZE:]  # Extract the ciphertext after the IV.
    cipher = AES.new(key, AES.MODE_OFB, iv=iv)  # Recreate AES with the same key and IV.
    plaintext = cipher.decrypt(ciphertext)  # Recover the original PDF/file bytes.

    filename = input_path.name
    if filename.startswith("EN-"):
        filename = filename[3:]
    if filename.endswith(".aes"):
        filename = filename[:-4]
    output_path = input_path.with_name(f"DE-{filename}")
    output_path.write_bytes(plaintext)  # Save the recovered file without deleting the source.
    return output_path


class AESFileApp:
    """Tkinter application for selecting, encrypting, and decrypting files."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("AES File Encryption - Lab 5")
        self.root.geometry("620x330")
        self.root.resizable(False, False)
        self.selected_file: Path | None = None

        self.build_ui()

    def build_ui(self) -> None:
        """Build the Arabic graphical interface."""
        frame = ttk.Frame(self.root, padding=22)
        frame.pack(fill="both", expand=True)

        title = ttk.Label(frame, text="واجهة تشفير وفك تشفير الملفات", font=("Arial", 18, "bold"))
        title.pack(pady=(0, 8))

        subtitle = ttk.Label(frame, text="AES-128 / OFB — مناسبة لملفات PDF والملفات الأخرى")
        subtitle.pack(pady=(0, 18))

        self.file_label = ttk.Label(frame, text="لم يتم اختيار ملف", foreground="#555555")
        self.file_label.pack(pady=8)

        select_button = ttk.Button(frame, text="اختيار ملف PDF أو ملف آخر", command=self.select_file)
        select_button.pack(fill="x", pady=6)

        self.encrypt_button = ttk.Button(frame, text="تشفير الملف", command=self.encrypt_selected)
        self.encrypt_button.pack(fill="x", pady=6)

        self.decrypt_button = ttk.Button(frame, text="فك تشفير الملف", command=self.decrypt_selected)
        self.decrypt_button.pack(fill="x", pady=6)

        self.status_label = ttk.Label(frame, text="المفتاح سيُحفظ في aes_key.bin بجانب البرنامج")
        self.status_label.pack(pady=16)

        note = ttk.Label(
            frame,
            text="تنبيه: لا تحذف aes_key.bin؛ يلزم استخدامه لفك التشفير.",
            foreground="#9b2c2c",
        )
        note.pack()

    def select_file(self) -> None:
        """Open a file picker and save the selected path."""
        path = filedialog.askopenfilename(
            title="اختر الملف",
            filetypes=[("PDF files", "*.pdf"), ("Encrypted files", "*.aes"), ("All files", "*.*")],
        )
        if path:
            self.selected_file = Path(path)
            self.file_label.config(text=str(self.selected_file))
            self.status_label.config(text="تم اختيار الملف، اختر عملية التشفير أو فك التشفير.")

    def encrypt_selected(self) -> None:
        """Encrypt the selected file without deleting the original."""
        if self.selected_file is None:
            messagebox.showwarning("تنبيه", "اختر ملفًا أولًا.")
            return
        try:
            output = encrypt_file(self.selected_file)
            self.status_label.config(text=f"تم التشفير: {output.name}")
            messagebox.showinfo("نجاح", f"تم تشفير الملف بنجاح.\n\nالناتج:\n{output}")
        except Exception as error:
            messagebox.showerror("خطأ", str(error))

    def decrypt_selected(self) -> None:
        """Decrypt the selected encrypted file without deleting the encrypted source."""
        if self.selected_file is None:
            messagebox.showwarning("تنبيه", "اختر ملفًا مشفرًا أولًا.")
            return
        try:
            output = decrypt_file(self.selected_file)
            self.status_label.config(text=f"تم فك التشفير: {output.name}")
            messagebox.showinfo("نجاح", f"تم فك التشفير بنجاح.\n\nالناتج:\n{output}")
        except Exception as error:
            messagebox.showerror("خطأ", str(error))


def main() -> None:
    """Start the graphical application."""
    root = tk.Tk()
    AESFileApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
