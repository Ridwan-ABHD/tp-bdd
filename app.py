# Interface graphique Tkinter

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from services import BilletterieService
from dao import init_database
import os


# --- Couleurs (thème clair) ---
class Colors:
    BG = "#f5f5f5"           # Fond gris clair
    BG_WHITE = "#ffffff"     # Blanc
    PRIMARY = "#3b82f6"      # Bleu
    SUCCESS = "#22c55e"      # Vert
    WARNING = "#f59e0b"      # Orange
    DANGER = "#ef4444"       # Rouge
    TEXT = "#1f2937"         # Texte foncé
    TEXT_LIGHT = "#6b7280"   # Texte gris
    BORDER = "#e5e7eb"       # Bordures


# --- Application principale ---
class BilletterieApp:
    
    def __init__(self, root):
        self.root = root
        self.root.title("Billetterie - Ridwan & Sébastien")
        
        # Taille de la fenêtre
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        win_w = min(1200, int(screen_w * 0.8))
        win_h = min(700, int(screen_h * 0.8))
        x = (screen_w - win_w) // 2
        y = (screen_h - win_h) // 2
        self.root.geometry(f"{win_w}x{win_h}+{x}+{y}")
        self.root.configure(bg=Colors.BG)
        
        # Service métier
        self.service = BilletterieService()
        
        # Interface
        self.create_interface()
        self.charger_stats()
        self.afficher_accueil()
        
        self.root.protocol("WM_DELETE_WINDOW", self.quitter)
    
    def create_interface(self):
        # Frame principale
        main = tk.Frame(self.root, bg=Colors.BG)
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # --- Sidebar à gauche avec scrollbar ---
        sidebar_container = tk.Frame(main, bg=Colors.BG_WHITE, width=220)
        sidebar_container.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        sidebar_container.pack_propagate(False)
        
        # Canvas pour le scroll
        canvas = tk.Canvas(sidebar_container, bg=Colors.BG_WHITE, 
                          highlightthickness=0, width=200)
        scrollbar = tk.Scrollbar(sidebar_container, orient="vertical", 
                                command=canvas.yview)
        
        sidebar = tk.Frame(canvas, bg=Colors.BG_WHITE)
        
        # Configurer le scroll
        sidebar.bind("<Configure>", 
                    lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=sidebar, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Scroll avec la molette
        def on_mousewheel(event):
            canvas.yview_scroll(-1 * (event.delta // 120), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Titre
        tk.Label(sidebar, text="🎫 Billetterie", font=("Arial", 16, "bold"),
                bg=Colors.BG_WHITE, fg=Colors.TEXT).pack(pady=20)
        
        # Boutons
        boutons = [
            ("📜 Lister ventes", self.lister_ventes),
            ("➕ Ajouter vente", self.ajouter_vente),
            ("🗑️ Supprimer vente", self.supprimer_vente),
            ("─" * 20, None),
            ("🎭 Événements", self.lister_evenements),
            ("👥 Acheteurs", self.lister_acheteurs),
            ("─" * 20, None),
            ("💰 Chiffre d'affaires", self.calculer_ca),
            ("📊 CA par événement", self.ca_par_evenement),
            ("📈 Taux remplissage", self.taux_remplissage),
            ("🏆 Top billets", self.top_billets),
            ("👑 Top acheteurs", self.top_acheteurs),
            ("─" * 20, None),
            ("🔄 Rafraîchir", self.rafraichir),
        ]
        
        for texte, commande in boutons:
            if commande is None:
                # Séparateur
                tk.Label(sidebar, text=texte, bg=Colors.BG_WHITE, 
                        fg=Colors.BORDER).pack(pady=5)
            else:
                btn = tk.Button(sidebar, text=texte, command=commande,
                               font=("Arial", 10), bg=Colors.BG_WHITE,
                               fg=Colors.TEXT, relief=tk.FLAT, anchor="w",
                               padx=15, pady=8, cursor="hand2")
                btn.pack(fill=tk.X, padx=10, pady=2)
                btn.bind("<Enter>", lambda e, b=btn: b.config(bg=Colors.BG))
                btn.bind("<Leave>", lambda e, b=btn: b.config(bg=Colors.BG_WHITE))
        
        # --- Zone principale à droite ---
        right = tk.Frame(main, bg=Colors.BG)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Cartes de stats en haut
        stats_frame = tk.Frame(right, bg=Colors.BG)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 3 cartes de stats
        self.card_ca = self.creer_carte(stats_frame, "Chiffre d'affaires", "0.00 €", Colors.SUCCESS)
        self.card_billets = self.creer_carte(stats_frame, "Billets vendus", "0", Colors.PRIMARY)
        self.card_events = self.creer_carte(stats_frame, "Événements", "0", Colors.WARNING)
        
        # Zone de texte pour les résultats
        result_frame = tk.Frame(right, bg=Colors.BG_WHITE)
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        self.result_text = tk.Text(result_frame, font=("Consolas", 10),
                                   bg=Colors.BG_WHITE, fg=Colors.TEXT,
                                   relief=tk.FLAT, padx=15, pady=15)
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(result_frame, command=self.result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=scrollbar.set)
        
        # Barre de statut en bas
        self.status_label = tk.Label(self.root, text="Prêt", font=("Arial", 9),
                                     bg=Colors.BG, fg=Colors.TEXT_LIGHT, anchor="w")
        self.status_label.pack(fill=tk.X, padx=10, pady=5)
    
    def creer_carte(self, parent, titre, valeur, couleur):
        """Crée une carte de statistique"""
        carte = tk.Frame(parent, bg=Colors.BG_WHITE, padx=20, pady=15)
        carte.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        tk.Label(carte, text=titre, font=("Arial", 10),
                bg=Colors.BG_WHITE, fg=Colors.TEXT_LIGHT).pack(anchor="w")
        
        label_val = tk.Label(carte, text=valeur, font=("Arial", 20, "bold"),
                            bg=Colors.BG_WHITE, fg=couleur)
        label_val.pack(anchor="w")
        
        return label_val
    
    def charger_stats(self):
        """Charge les statistiques dans les cartes"""
        try:
            stats = self.service.calculer_indicateurs_avances()
            self.card_ca.config(text=f"{stats['chiffre_affaires_total']:.2f} €")
            self.card_billets.config(text=str(stats['quantite_totale']))
            self.card_events.config(text=str(stats['nombre_evenements']))
        except:
            pass
    
    def afficher(self, titre, contenu):
        """Affiche du contenu dans la zone de texte"""
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, f"{titre}\n")
        self.result_text.insert(tk.END, "=" * 50 + "\n\n")
        self.result_text.insert(tk.END, contenu)
    
    def set_status(self, message):
        """Met à jour la barre de statut"""
        self.status_label.config(text=message)
    
    def afficher_accueil(self):
        """Affiche le message d'accueil"""
        self.afficher("Bienvenue", 
            "Application de gestion de billetterie\n\n"
            "Utilisez les boutons à gauche pour naviguer.\n\n"
            "Fonctionnalités :\n"
            "  - Gestion des ventes (ajouter, supprimer, lister)\n"
            "  - Consultation des événements et acheteurs\n"
            "  - Statistiques et indicateurs\n"
        )
    
    # --- Actions ---
    
    def rafraichir(self):
        """Rafraîchit les données"""
        self.charger_stats()
        self.lister_ventes()
        self.set_status("Données rafraîchies")
    
    def lister_ventes(self):
        """Liste toutes les ventes"""
        ventes = self.service.lister_ventes()
        
        if not ventes:
            self.afficher("Liste des ventes", "Aucune vente enregistrée.")
            return
        
        contenu = f"Total : {len(ventes)} vente(s)\n\n"
        for v in ventes:
            contenu += f"[#{v['id_vente']}] {v['acheteur']}\n"
            contenu += f"   Événement : {v['evenement']}\n"
            contenu += f"   Billet : {v['type_billet']} x{v['quantite']}\n"
            contenu += f"   Montant : {v['montant_total']:.2f}€\n"
            contenu += f"   Date : {v['date_vente']}\n\n"
        
        self.afficher("Liste des ventes", contenu)
        self.set_status(f"{len(ventes)} vente(s) trouvée(s)")
    
    def ajouter_vente(self):
        """Ouvre le dialogue pour ajouter une vente"""
        dialog = DialogVente(self.root, self.service)
        
        if dialog.result:
            result = self.service.effectuer_vente(
                dialog.result['id_acheteur'],
                dialog.result['id_type_billet'],
                dialog.result['quantite']
            )
            
            if result['success']:
                self.charger_stats()
                self.afficher("Vente ajoutée", 
                    f"Vente #{result['id_vente']} créée avec succès!\n\n"
                    f"Montant : {result['montant_total']:.2f}€"
                )
                self.set_status("Vente ajoutée")
            else:
                messagebox.showerror("Erreur", result['error'])
    
    def supprimer_vente(self):
        """Supprime une vente"""
        id_str = simpledialog.askstring("Supprimer", "ID de la vente à supprimer :",
                                        parent=self.root)
        if not id_str:
            return
        
        try:
            id_vente = int(id_str)
        except ValueError:
            messagebox.showerror("Erreur", "L'ID doit être un nombre")
            return
        
        if messagebox.askyesno("Confirmer", f"Supprimer la vente #{id_vente} ?"):
            result = self.service.annuler_vente(id_vente)
            
            if result['success']:
                self.charger_stats()
                self.afficher("Vente supprimée", 
                    f"La vente #{id_vente} a été supprimée.\n"
                    "Les billets ont été remis en stock."
                )
                self.set_status("Vente supprimée")
            else:
                messagebox.showerror("Erreur", result['error'])
    
    def lister_evenements(self):
        """Liste les événements"""
        events = self.service.lister_evenements()
        
        contenu = f"Total : {len(events)} événement(s)\n\n"
        for e in events:
            contenu += f"[#{e['id_evenement']}] {e['nom']}\n"
            contenu += f"   Date : {e['date_evenement']} à {e['heure_debut']}\n"
            contenu += f"   Lieu : {e['lieu']}\n"
            contenu += f"   Catégorie : {e['categorie']}\n"
            contenu += f"   Capacité : {e['capacite_max']} places\n\n"
        
        self.afficher("Liste des événements", contenu)
        self.set_status(f"{len(events)} événement(s)")
    
    def lister_acheteurs(self):
        """Liste les acheteurs"""
        acheteurs = self.service.lister_acheteurs()
        
        contenu = f"Total : {len(acheteurs)} acheteur(s)\n\n"
        for a in acheteurs:
            contenu += f"[#{a['id_acheteur']}] {a['nom']} {a['prenom']}\n"
            contenu += f"   Email : {a['email']}\n"
            if a['telephone']:
                contenu += f"   Tél : {a['telephone']}\n"
            contenu += "\n"
        
        self.afficher("Liste des acheteurs", contenu)
        self.set_status(f"{len(acheteurs)} acheteur(s)")
    
    def calculer_ca(self):
        """Affiche le chiffre d'affaires total"""
        data = self.service.calculer_chiffre_affaires_total()
        ca = data['chiffre_affaires_total']
        quantite = data['quantite_totale_vendue']
        panier = data['panier_moyen']
        
        contenu = f"CA Total : {ca:.2f} €\n\n"
        contenu += f"Billets vendus : {quantite}\n"
        contenu += f"Panier moyen : {panier:.2f} €"
        
        self.afficher("Chiffre d'affaires total", contenu)
        self.set_status("CA calculé")
    
    def ca_par_evenement(self):
        """Affiche le CA par événement"""
        data = self.service.calculer_ca_par_evenement()
        
        contenu = ""
        for e in data:
            contenu += f"{e['evenement']}\n"
            contenu += f"   CA : {e['chiffre_affaires']:.2f}€\n"
            contenu += f"   Billets vendus : {e['billets_vendus']}\n\n"
        
        self.afficher("CA par événement", contenu if contenu else "Aucune donnée")
        self.set_status("CA par événement")
    
    def taux_remplissage(self):
        """Affiche le taux de remplissage"""
        data = self.service.calculer_taux_remplissage()
        
        contenu = ""
        for e in data:
            contenu += f"{e['evenement']}\n"
            contenu += f"   Vendus : {e['billets_vendus']} / {e['capacite_max']}\n"
            contenu += f"   Taux : {e['taux_remplissage']:.1f}%\n\n"
        
        self.afficher("Taux de remplissage", contenu if contenu else "Aucune donnée")
        self.set_status("Taux de remplissage")
    
    def top_billets(self):
        """Affiche le classement des billets"""
        data = self.service.obtenir_top_billets()
        
        contenu = ""
        for i, b in enumerate(data, 1):
            contenu += f"#{i} {b['nom_type']} ({b['evenement']})\n"
            contenu += f"   Vendus : {b['total_vendu']}\n"
            contenu += f"   CA : {b['ca_type']:.2f}€\n\n"
        
        self.afficher("Top billets vendus", contenu if contenu else "Aucune donnée")
        self.set_status("Top billets")
    
    def top_acheteurs(self):
        """Affiche le top des acheteurs"""
        data = self.service.obtenir_top_acheteurs()
        
        contenu = ""
        for i, a in enumerate(data, 1):
            contenu += f"#{i} {a['acheteur']}\n"
            contenu += f"   Achats : {a['nombre_achats']}\n"
            contenu += f"   Billets : {a['total_billets']}\n"
            contenu += f"   Total dépensé : {a['total_depense']:.2f}€\n\n"
        
        self.afficher("Top acheteurs", contenu if contenu else "Aucune donnée")
        self.set_status("Top acheteurs")
    
    def quitter(self):
        """Ferme l'application proprement"""
        self.service.fermer_connexion()
        self.root.destroy()


# --- Dialogue pour ajouter une vente ---
class DialogVente(tk.Toplevel):
    
    def __init__(self, parent, service):
        super().__init__(parent)
        
        self.service = service
        self.result = None
        
        self.title("Nouvelle vente")
        self.geometry("350x280")
        self.configure(bg=Colors.BG_WHITE)
        self.resizable(False, False)
        
        # Centrer
        self.transient(parent)
        self.grab_set()
        
        # Contenu
        self.creer_formulaire()
        
        self.wait_window()
    
    def creer_formulaire(self):
        # Titre
        tk.Label(self, text="Nouvelle vente", font=("Arial", 14, "bold"),
                bg=Colors.BG_WHITE, fg=Colors.TEXT).pack(pady=15)
        
        form = tk.Frame(self, bg=Colors.BG_WHITE)
        form.pack(padx=30, fill=tk.X)
        
        # ID Acheteur
        tk.Label(form, text="ID Acheteur", bg=Colors.BG_WHITE, 
                fg=Colors.TEXT_LIGHT).pack(anchor="w")
        self.entry_acheteur = tk.Entry(form, font=("Arial", 11))
        self.entry_acheteur.pack(fill=tk.X, pady=(0, 10))
        
        # ID Type Billet
        tk.Label(form, text="ID Type Billet", bg=Colors.BG_WHITE,
                fg=Colors.TEXT_LIGHT).pack(anchor="w")
        self.entry_billet = tk.Entry(form, font=("Arial", 11))
        self.entry_billet.pack(fill=tk.X, pady=(0, 10))
        
        # Quantité
        tk.Label(form, text="Quantité", bg=Colors.BG_WHITE,
                fg=Colors.TEXT_LIGHT).pack(anchor="w")
        self.entry_quantite = tk.Entry(form, font=("Arial", 11))
        self.entry_quantite.pack(fill=tk.X, pady=(0, 10))
        self.entry_quantite.insert(0, "1")
        
        # Boutons
        btn_frame = tk.Frame(self, bg=Colors.BG_WHITE)
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Annuler", command=self.destroy,
                 bg=Colors.BG, fg=Colors.TEXT).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Confirmer", command=self.confirmer,
                 bg=Colors.PRIMARY, fg="white").pack(side=tk.LEFT, padx=5)
    
    def confirmer(self):
        try:
            self.result = {
                'id_acheteur': int(self.entry_acheteur.get()),
                'id_type_billet': int(self.entry_billet.get()),
                'quantite': int(self.entry_quantite.get())
            }
            self.destroy()
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des nombres valides")


# --- Point d'entrée ---
def main():
    from config import DATABASE_PATH
    
    # Créer la base si elle n'existe pas
    if not os.path.exists(DATABASE_PATH):
        print("Initialisation de la base...")
        init_database()
    
    root = tk.Tk()
    app = BilletterieApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
