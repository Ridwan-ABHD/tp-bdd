"""
Interface graphique Tkinter - Application Billetterie
Projet : Gestion de billetterie locale
Auteurs : Ridwan & Sébastien

IMPORTANT : L'UI n'écrit JAMAIS de SQL directement
Elle utilise uniquement les services métier
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from services import BilletterieService
from dao import init_database
import os


class BilletterieApp:
    """Application principale de gestion de billetterie"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🎫 Gestion de Billetterie Locale")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f0f0")
        
        # Service métier (pas d'accès direct à la base!)
        self.service = BilletterieService()
        
        # Configuration du style
        self.setup_styles()
        
        # Construction de l'interface
        self.create_header()
        self.create_main_content()
        self.create_status_bar()
        
        # Gestion de la fermeture
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_styles(self):
        """Configure les styles de l'application"""
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("Header.TLabel", font=("Helvetica", 16, "bold"), background="#2c3e50", foreground="white")
        style.configure("Action.TButton", font=("Helvetica", 10), padding=10)
        style.configure("Stats.TButton", font=("Helvetica", 10), padding=10, background="#27ae60")
    
    def create_header(self):
        """Crée l'en-tête de l'application"""
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title = tk.Label(
            header_frame, 
            text="🎫 Système de Billetterie - Ridwan & Sébastien",
            font=("Helvetica", 18, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title.pack(pady=15)
    
    def create_main_content(self):
        """Crée le contenu principal avec les boutons et l'affichage"""
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Frame gauche - Boutons d'action
        left_frame = tk.LabelFrame(main_frame, text="Actions", font=("Helvetica", 12, "bold"), bg="#f0f0f0")
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # === SECTION GESTION ===
        tk.Label(left_frame, text="📋 Gestion", font=("Helvetica", 11, "bold"), bg="#f0f0f0").pack(pady=(10, 5))
        
        # Bouton: Ajouter vente (équivalent POST /vente)
        ttk.Button(
            left_frame, 
            text="➕ Ajouter Vente",
            command=self.ajouter_vente,
            style="Action.TButton",
            width=25
        ).pack(pady=5, padx=10)
        
        # Bouton: Lister ventes (équivalent GET /ventes)
        ttk.Button(
            left_frame, 
            text="📜 Lister Ventes",
            command=self.lister_ventes,
            style="Action.TButton",
            width=25
        ).pack(pady=5, padx=10)
        
        # Bouton: Lister événements
        ttk.Button(
            left_frame, 
            text="🎭 Lister Événements",
            command=self.lister_evenements,
            style="Action.TButton",
            width=25
        ).pack(pady=5, padx=10)
        
        # Bouton: Lister acheteurs
        ttk.Button(
            left_frame, 
            text="👥 Lister Acheteurs",
            command=self.lister_acheteurs,
            style="Action.TButton",
            width=25
        ).pack(pady=5, padx=10)
        
        # === SECTION STATISTIQUES ===
        tk.Label(left_frame, text="📊 Statistiques", font=("Helvetica", 11, "bold"), bg="#f0f0f0").pack(pady=(20, 5))
        
        # Bouton: Calcul CA (équivalent GET /stats/ca)
        ttk.Button(
            left_frame, 
            text="💰 Calcul CA",
            command=self.calculer_ca,
            style="Stats.TButton",
            width=25
        ).pack(pady=5, padx=10)
        
        # Bouton: Produit top (équivalent GET /stats/top)
        ttk.Button(
            left_frame, 
            text="🏆 Billets Top",
            command=self.afficher_top_billets,
            style="Stats.TButton",
            width=25
        ).pack(pady=5, padx=10)
        
        # Bouton: Taux de remplissage
        ttk.Button(
            left_frame, 
            text="📈 Taux Remplissage",
            command=self.afficher_taux_remplissage,
            style="Stats.TButton",
            width=25
        ).pack(pady=5, padx=10)
        
        # Bouton: CA par événement
        ttk.Button(
            left_frame, 
            text="🎯 CA par Événement",
            command=self.afficher_ca_evenement,
            style="Stats.TButton",
            width=25
        ).pack(pady=5, padx=10)
        
        # Bouton: Indicateurs avancés
        ttk.Button(
            left_frame, 
            text="🔬 Indicateurs Avancés",
            command=self.afficher_indicateurs_avances,
            style="Stats.TButton",
            width=25
        ).pack(pady=5, padx=10)
        
        # === SECTION ADMINISTRATION ===
        tk.Label(left_frame, text="⚙️ Administration", font=("Helvetica", 11, "bold"), bg="#f0f0f0").pack(pady=(20, 5))
        
        ttk.Button(
            left_frame, 
            text="🔄 Réinitialiser Base",
            command=self.reinitialiser_base,
            width=25
        ).pack(pady=5, padx=10)
        
        # Frame droite - Zone d'affichage
        right_frame = tk.LabelFrame(main_frame, text="Résultats", font=("Helvetica", 12, "bold"), bg="#f0f0f0")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Zone de texte avec scrollbar
        text_frame = tk.Frame(right_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.result_text = tk.Text(
            text_frame, 
            wrap=tk.WORD, 
            font=("Consolas", 10),
            yscrollcommand=scrollbar.set
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.result_text.yview)
        
        # Message initial
        self.afficher_message("Bienvenue dans l'application de Billetterie!\n\n"
                             "Utilisez les boutons à gauche pour effectuer des actions.\n\n"
                             "Équivalences API:\n"
                             "• Ajouter Vente → POST /vente\n"
                             "• Lister Ventes → GET /ventes\n"
                             "• Calcul CA → GET /stats/ca\n"
                             "• Billets Top → GET /stats/top")
    
    def create_status_bar(self):
        """Crée la barre de statut"""
        self.status_bar = tk.Label(
            self.root, 
            text="Prêt", 
            bd=1, 
            relief=tk.SUNKEN, 
            anchor=tk.W,
            font=("Helvetica", 9),
            bg="#ecf0f1"
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def afficher_message(self, message: str):
        """Affiche un message dans la zone de résultats"""
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, message)
    
    def set_status(self, message: str):
        """Met à jour la barre de statut"""
        self.status_bar.config(text=message)
    
    # ============================================
    # Actions - Gestion
    # ============================================
    
    def ajouter_vente(self):
        """Ajoute une vente (POST /vente)"""
        self.set_status("Ajout d'une vente...")
        
        # Dialogue pour saisir les informations
        dialog = VenteDialog(self.root, self.service)
        if dialog.result:
            result = self.service.effectuer_vente(
                dialog.result['id_acheteur'],
                dialog.result['id_type_billet'],
                dialog.result['quantite']
            )
            
            if result['success']:
                messagebox.showinfo("Succès", result['message'])
                self.afficher_message(f"✅ Vente effectuée!\n\n"
                                     f"ID Vente: {result['id_vente']}\n"
                                     f"Montant: {result['montant_total']:.2f}€")
            else:
                messagebox.showerror("Erreur", result['error'])
        
        self.set_status("Prêt")
    
    def lister_ventes(self):
        """Liste les ventes (GET /ventes)"""
        self.set_status("Chargement des ventes...")
        
        ventes = self.service.lister_ventes()
        
        if not ventes:
            self.afficher_message("Aucune vente enregistrée.")
        else:
            output = "📜 LISTE DES VENTES\n" + "=" * 60 + "\n\n"
            for v in ventes:
                output += f"🎫 Vente #{v['id_vente']}\n"
                output += f"   Événement: {v['evenement']}\n"
                output += f"   Type: {v['type_billet']} ({v['prix_unitaire']:.2f}€)\n"
                output += f"   Acheteur: {v['acheteur']}\n"
                output += f"   Quantité: {v['quantite']}\n"
                output += f"   Montant: {v['montant_total']:.2f}€\n"
                output += f"   Date: {v['date_vente']}\n"
                output += "-" * 40 + "\n"
            
            output += f"\nTotal: {len(ventes)} vente(s)"
            self.afficher_message(output)
        
        self.set_status(f"{len(ventes)} vente(s) trouvée(s)")
    
    def lister_evenements(self):
        """Liste les événements"""
        self.set_status("Chargement des événements...")
        
        evenements = self.service.lister_evenements()
        
        if not evenements:
            self.afficher_message("Aucun événement enregistré.")
        else:
            output = "🎭 LISTE DES ÉVÉNEMENTS\n" + "=" * 60 + "\n\n"
            for e in evenements:
                output += f"🎪 {e['nom']}\n"
                output += f"   Catégorie: {e['categorie']}\n"
                output += f"   Date: {e['date_evenement']} à {e['heure_debut']}\n"
                output += f"   Lieu: {e['lieu']}\n"
                output += f"   Capacité max: {e['capacite_max']} places\n"
                output += "-" * 40 + "\n"
            
            self.afficher_message(output)
        
        self.set_status(f"{len(evenements)} événement(s) trouvé(s)")
    
    def lister_acheteurs(self):
        """Liste les acheteurs"""
        self.set_status("Chargement des acheteurs...")
        
        acheteurs = self.service.lister_acheteurs()
        
        if not acheteurs:
            self.afficher_message("Aucun acheteur enregistré.")
        else:
            output = "👥 LISTE DES ACHETEURS\n" + "=" * 60 + "\n\n"
            for a in acheteurs:
                output += f"👤 {a['prenom']} {a['nom']}\n"
                output += f"   Email: {a['email']}\n"
                output += f"   Tél: {a['telephone'] or 'Non renseigné'}\n"
                output += f"   Inscrit le: {a['date_inscription']}\n"
                output += "-" * 40 + "\n"
            
            self.afficher_message(output)
        
        self.set_status(f"{len(acheteurs)} acheteur(s) trouvé(s)")
    
    # ============================================
    # Actions - Statistiques
    # ============================================
    
    def calculer_ca(self):
        """Calcule le CA total (GET /stats/ca)"""
        self.set_status("Calcul du chiffre d'affaires...")
        
        stats = self.service.calculer_chiffre_affaires_total()
        
        output = "💰 CHIFFRE D'AFFAIRES\n" + "=" * 60 + "\n\n"
        output += f"📊 CA Total: {stats['chiffre_affaires_total']:.2f}€\n\n"
        output += f"🎫 Billets vendus: {stats['quantite_totale_vendue']}\n\n"
        output += f"🛒 Panier moyen: {stats['panier_moyen']:.2f}€\n"
        
        self.afficher_message(output)
        self.set_status("Calcul terminé")
    
    def afficher_top_billets(self):
        """Affiche le top des billets vendus (GET /stats/top)"""
        self.set_status("Chargement du classement...")
        
        top_billets = self.service.obtenir_top_billets()
        
        if not top_billets:
            self.afficher_message("Aucune donnée de vente disponible.")
        else:
            output = "🏆 TOP BILLETS VENDUS\n" + "=" * 60 + "\n\n"
            for i, b in enumerate(top_billets, 1):
                output += f"{i}. {b['nom_type']} - {b['evenement']}\n"
                output += f"   Quantité vendue: {b['total_vendu']}\n"
                output += f"   CA généré: {b['ca_type']:.2f}€\n"
                output += "-" * 40 + "\n"
            
            self.afficher_message(output)
        
        self.set_status("Classement affiché")
    
    def afficher_taux_remplissage(self):
        """Affiche le taux de remplissage par événement"""
        self.set_status("Calcul des taux de remplissage...")
        
        taux = self.service.calculer_taux_remplissage()
        
        if not taux:
            self.afficher_message("Aucun événement disponible.")
        else:
            output = "📈 TAUX DE REMPLISSAGE\n" + "=" * 60 + "\n\n"
            for t in taux:
                barre = "█" * int(t['taux_remplissage'] / 5) + "░" * (20 - int(t['taux_remplissage'] / 5))
                output += f"🎪 {t['evenement']}\n"
                output += f"   [{barre}] {t['taux_remplissage']}%\n"
                output += f"   Vendus: {t['billets_vendus']} / {t['capacite_max']}\n"
                output += "-" * 40 + "\n"
            
            self.afficher_message(output)
        
        self.set_status("Taux calculés")
    
    def afficher_ca_evenement(self):
        """Affiche le CA par événement"""
        self.set_status("Calcul du CA par événement...")
        
        ca_evenements = self.service.calculer_ca_par_evenement()
        
        if not ca_evenements:
            self.afficher_message("Aucun événement disponible.")
        else:
            output = "🎯 CA PAR ÉVÉNEMENT\n" + "=" * 60 + "\n\n"
            for e in ca_evenements:
                output += f"🎪 {e['evenement']} ({e['categorie']})\n"
                output += f"   Date: {e['date_evenement']}\n"
                output += f"   CA: {e['chiffre_affaires']:.2f}€\n"
                output += f"   Billets vendus: {e['billets_vendus']}\n"
                output += "-" * 40 + "\n"
            
            self.afficher_message(output)
        
        self.set_status("CA par événement affiché")
    
    def afficher_indicateurs_avances(self):
        """Affiche les indicateurs avancés calculés en Python"""
        self.set_status("Calcul des indicateurs avancés...")
        
        indicateurs = self.service.calculer_indicateurs_avances()
        
        output = "🔬 INDICATEURS AVANCÉS\n" + "=" * 60 + "\n\n"
        output += f"💰 Chiffre d'affaires total: {indicateurs['chiffre_affaires_total']:.2f}€\n\n"
        output += f"🎫 Billets vendus: {indicateurs['quantite_totale']}\n\n"
        output += f"💵 Prix moyen par billet: {indicateurs['prix_moyen_billet']:.2f}€\n\n"
        output += f"📊 CA moyen par événement: {indicateurs['ca_moyen_par_evenement']:.2f}€\n\n"
        output += f"📈 Taux de remplissage moyen: {indicateurs['taux_remplissage_moyen']:.2f}%\n\n"
        output += f"🏆 Événement le plus rentable: {indicateurs['evenement_top']}\n\n"
        output += f"📅 Date d'analyse: {indicateurs['date_analyse']}\n"
        
        self.afficher_message(output)
        self.set_status("Indicateurs calculés")
    
    # ============================================
    # Administration
    # ============================================
    
    def reinitialiser_base(self):
        """Réinitialise la base de données"""
        if messagebox.askyesno("Confirmation", 
                               "Êtes-vous sûr de vouloir réinitialiser la base?\n"
                               "Toutes les données seront perdues!"):
            if init_database():
                messagebox.showinfo("Succès", "Base de données réinitialisée")
                self.afficher_message("✅ Base de données réinitialisée avec succès!")
            else:
                messagebox.showerror("Erreur", "Erreur lors de la réinitialisation")
    
    def on_closing(self):
        """Gestion de la fermeture de l'application"""
        self.service.fermer_connexion()
        self.root.destroy()


class VenteDialog(simpledialog.Dialog):
    """Dialogue pour ajouter une vente"""
    
    def __init__(self, parent, service):
        self.service = service
        self.result = None
        super().__init__(parent, "Nouvelle Vente")
    
    def body(self, master):
        """Crée le contenu du dialogue"""
        tk.Label(master, text="ID Acheteur:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.acheteur_entry = tk.Entry(master)
        self.acheteur_entry.grid(row=0, column=1, pady=5)
        
        tk.Label(master, text="ID Type Billet:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.billet_entry = tk.Entry(master)
        self.billet_entry.grid(row=1, column=1, pady=5)
        
        tk.Label(master, text="Quantité:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.quantite_entry = tk.Entry(master)
        self.quantite_entry.grid(row=2, column=1, pady=5)
        self.quantite_entry.insert(0, "1")
        
        return self.acheteur_entry
    
    def apply(self):
        """Applique les valeurs saisies"""
        try:
            self.result = {
                'id_acheteur': int(self.acheteur_entry.get()),
                'id_type_billet': int(self.billet_entry.get()),
                'quantite': int(self.quantite_entry.get())
            }
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des valeurs numériques valides")
            self.result = None


def main():
    """Point d'entrée de l'application"""
    # Initialiser la base si elle n'existe pas
    from config import DATABASE_PATH
    if not os.path.exists(DATABASE_PATH):
        print("Initialisation de la base de données...")
        init_database()
    
    # Lancer l'application
    root = tk.Tk()
    app = BilletterieApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
