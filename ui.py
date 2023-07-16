import tkinter as tk
import tkinter.font as tkFont
import suggestion

def generate_corrections():
    input_text = input_text_box.get("1.0", "end-1c")
    corrected_text = suggestion.get_output(input_text)  
    output_text_box.config(state="normal")  
    output_text_box.delete("1.0", tk.END)
    output_text_box.insert(tk.END, corrected_text)


    output_text_box.config(state="disabled") 


def change_font_size(delta):
    current_font = tkFont.Font(font=input_text_box.cget("font"))
    new_size = current_font.actual()["size"] + delta
    new_font = current_font.copy()
    new_font.configure(size=new_size)
    input_text_box.configure(font=new_font)
    output_text_box.configure(font=new_font)

def increase_font_size():
    change_font_size(1)

def decrease_font_size():
    change_font_size(-1)

root = tk.Tk()
root.title("Chinese Writing Assistant")
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.rowconfigure(0, weight=1)

input_frame = tk.Frame(root)
input_frame.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="nsew")
input_frame.columnconfigure(0, weight=1)
input_frame.rowconfigure(1, weight=1)
input_label = tk.Label(input_frame, text="Input Text:")
input_label.grid(row=0, column=0, sticky="nw")
input_text_box = tk.Text(input_frame, wrap=tk.WORD)
input_text_box.grid(row=1, column=0, sticky="nsew")

output_frame = tk.Frame(root)
output_frame.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="nsew")
output_frame.columnconfigure(0, weight=1)
output_frame.rowconfigure(1, weight=1)
output_label = tk.Label(output_frame, text="Corrected Text:")
output_label.grid(row=0, column=0, sticky="nw")
output_text_box = tk.Text(output_frame, wrap=tk.WORD, state="disabled")
output_text_box.grid(row=1, column=0, sticky="nsew")
output_text_box.tag_configure("underline", foreground="red", underline=True)

font_buttons_frame = tk.Frame(root)
font_buttons_frame.grid(row=2, column=0, pady=(5, 10))
increase_font_button = tk.Button(font_buttons_frame, text="Text Size +", command=increase_font_size)
increase_font_button.pack(side=tk.LEFT, padx=(0, 5))
decrease_font_button = tk.Button(font_buttons_frame, text="Text Size -", command=decrease_font_size)
decrease_font_button.pack(side=tk.LEFT)

generate_button = tk.Button(root, text="Generate Corrections", command=generate_corrections)
generate_button.grid(row=2, column=1, pady=(5, 10))

root.mainloop()


