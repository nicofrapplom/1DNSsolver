

def log_message(category, message, io_control):
    """
    Print the message if the cathegory is enabled in io_control
    """
    if not io_control.get("log", True):
        return  # logging globale disattivato

    flag_name = f"log_{category.lower()}"
    if io_control.get(flag_name, False):  # controlla la categoria
        print(f"[INFO {category.upper()}] - {message}")