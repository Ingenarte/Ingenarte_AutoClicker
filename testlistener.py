from pynput import keyboard

_current_mods = set()

def _on_key_press(key):
    # Por ejemplo, detectar Alt + A
    if key in (keyboard.Key.alt_l, keyboard.Key.alt_r):
        _current_mods.add(key)
    if keyboard.Key.alt_l in _current_mods and getattr(key, "char", "").lower() == "q":
        print("¡Se detectó Alt+A!")

def _on_key_release(key):
    if key in _current_mods:
        _current_mods.remove(key)

with keyboard.Listener(on_press=_on_key_press, on_release=_on_key_release) as listener:
    print("Listener activo: presiona Alt+A para probar")
    listener.join()
