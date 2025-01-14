from colorama import init, Fore

init(autoreset=True)

def ctext(text_type, text):
    color_map = {
        'success': Fore.GREEN,   # Успех - зеленый
        'error': Fore.RED,       # Ошибка - красный
        'warning': Fore.YELLOW,  # Предупреждение - желтый
        'info': Fore.CYAN,       # Информация - голубой
    }
    color = color_map.get(text_type, Fore.WHITE)
    
    print(color + text)
    return 1