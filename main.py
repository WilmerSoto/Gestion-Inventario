import ttkbootstrap as ttk
from ui.main_window import VentanaPrincipal
from data.repositories import RepositorioTransacciones

if __name__ == "__main__":
    root = ttk.Window(themename="superhero")
    
    path = "~/Documents/Gestion Ingresos-Egresos/transacciones.json"
    repo_transacciones = RepositorioTransacciones(path)
    
    app = VentanaPrincipal(root, repo_transacciones)
    root.mainloop()