"""
Interface graphique Tkinter - Application Billetterie
🎨 DESIGN PREMIUM EDITION 🎨
Projet : Gestion de billetterie locale
Auteurs : Ridwan & Sébastien

DESIGN: Dark Mode / Glassmorphism / Modern UI
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from services import BilletterieService
from dao import init_database
import os
import math


# ============================================
# 🎨 PALETTE DE COULEURS PREMIUM
# ============================================
class Colors:
    # Fond principal - Dégradé sombre
    BG_DARK = "#0a0a0f"
    BG_DARKER = "#05050a"
    BG_CARD = "#12121a"
    BG_CARD_HOVER = "#1a1a25"
    
    # Accent colors - Néon/Cyber
    PRIMARY = "#6366f1"        # Indigo vif
    PRIMARY_LIGHT = "#818cf8"
    PRIMARY_DARK = "#4f46e5"
    
    SECONDARY = "#06b6d4"      # Cyan néon
    SECONDARY_LIGHT = "#22d3ee"
    
    ACCENT = "#f43f5e"         # Rose/Rouge vif
    ACCENT_LIGHT = "#fb7185"
    
    SUCCESS = "#10b981"        # Vert émeraude
    SUCCESS_LIGHT = "#34d399"
    
    WARNING = "#f59e0b"        # Orange ambre
    GOLD = "#fbbf24"
    
    # Texte
    TEXT_PRIMARY = "#f8fafc"
    TEXT_SECONDARY = "#94a3b8"
    TEXT_MUTED = "#64748b"
    
    # Bordures et effets
    BORDER = "#1e293b"
    BORDER_LIGHT = "#334155"
    GLOW = "#6366f1"
    
    # Glassmorphism
    GLASS = "#ffffff0a"
    GLASS_BORDER = "#ffffff15"


# ============================================
# 🎨 COMPOSANTS UI CUSTOM
# ============================================
class GlowButton(tk.Canvas):
    """Bouton avec effet de glow néon"""
    
    def __init__(self, parent, text, command, color=Colors.PRIMARY, width=220, height=50, **kwargs):
        super().__init__(parent, width=width, height=height, 
                        bg=Colors.BG_CARD, highlightthickness=0, **kwargs)
        
        self.command = command
        self.color = color
        self.text = text
        self.width = width
        self.height = height
        self.is_hovered = False
        self.glow_intensity = 0
        
        self.draw_button()
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        self.bind("<ButtonRelease-1>", self.on_release)
    
    def draw_button(self):
        self.delete("all")
        
        # Glow effect (cercles concentriques)
        if self.glow_intensity > 0:
            for i in range(5):
                alpha = int(self.glow_intensity * (5-i) / 5)
                glow_color = self._blend_color(Colors.BG_CARD, self.color, alpha/100)
                self.create_rounded_rect(
                    5-i*2, 5-i*2, self.width-5+i*2, self.height-5+i*2,
                    radius=15+i*2, fill=glow_color, outline=""
                )
        
        # Bouton principal
        bg_color = self._blend_color(Colors.BG_CARD, self.color, 20 if self.is_hovered else 10)
        self.create_rounded_rect(5, 5, self.width-5, self.height-5, 
                                radius=12, fill=bg_color, 
                                outline=self.color if self.is_hovered else Colors.BORDER,
                                width=2 if self.is_hovered else 1)
        
        # Ligne de glow en haut
        if self.is_hovered:
            self.create_line(20, 7, self.width-20, 7, fill=self.color, width=2)
        
        # Texte
        self.create_text(self.width//2, self.height//2, text=self.text,
                        font=("Segoe UI", 11, "bold"), 
                        fill=Colors.TEXT_PRIMARY if self.is_hovered else Colors.TEXT_SECONDARY)
    
    def create_rounded_rect(self, x1, y1, x2, y2, radius=10, **kwargs):
        points = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1,
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def _blend_color(self, color1, color2, amount):
        """Mélange deux couleurs"""
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
        
        r = int(r1 + (r2-r1) * amount / 100)
        g = int(g1 + (g2-g1) * amount / 100)
        b = int(b1 + (b2-b1) * amount / 100)
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def on_enter(self, event):
        self.is_hovered = True
        self.animate_glow(True)
    
    def on_leave(self, event):
        self.is_hovered = False
        self.animate_glow(False)
    
    def animate_glow(self, entering):
        target = 50 if entering else 0
        step = 5 if entering else -5
        
        def animate():
            self.glow_intensity += step
            if (entering and self.glow_intensity < target) or \
               (not entering and self.glow_intensity > target):
                self.draw_button()
                self.after(20, animate)
            else:
                self.glow_intensity = target
                self.draw_button()
        
        animate()
    
    def on_click(self, event):
        self.glow_intensity = 80
        self.draw_button()
    
    def on_release(self, event):
        self.glow_intensity = 50
        self.draw_button()
        if self.command:
            self.command()


class NeonCard(tk.Frame):
    """Carte avec effet néon sur les bords"""
    
    def __init__(self, parent, title="", icon="", accent_color=Colors.PRIMARY, **kwargs):
        super().__init__(parent, bg=Colors.BG_CARD, **kwargs)
        
        self.accent_color = accent_color
        self.configure(highlightbackground=Colors.BORDER, highlightthickness=1)
        
        # Header de la carte
        header = tk.Frame(self, bg=Colors.BG_CARD)
        header.pack(fill=tk.X, padx=15, pady=(15, 10))
        
        # Icône et titre
        title_text = f"{icon}  {title}" if icon else title
        self.title_label = tk.Label(
            header, text=title_text,
            font=("Segoe UI", 13, "bold"),
            bg=Colors.BG_CARD, fg=accent_color
        )
        self.title_label.pack(side=tk.LEFT)
        
        # Ligne décorative
        line_frame = tk.Frame(self, bg=Colors.BG_CARD, height=2)
        line_frame.pack(fill=tk.X, padx=15)
        
        line = tk.Frame(line_frame, bg=accent_color, height=2, width=50)
        line.pack(side=tk.LEFT)
        
        line2 = tk.Frame(line_frame, bg=Colors.BORDER, height=1)
        line2.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=1)
        
        # Zone de contenu
        self.content = tk.Frame(self, bg=Colors.BG_CARD)
        self.content.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Effet de survol
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
    
    def on_enter(self, event):
        self.configure(highlightbackground=self.accent_color)
    
    def on_leave(self, event):
        self.configure(highlightbackground=Colors.BORDER)


class StatCard(tk.Frame):
    """Carte de statistique animée"""
    
    def __init__(self, parent, title, value, icon, color=Colors.PRIMARY, **kwargs):
        super().__init__(parent, bg=Colors.BG_CARD, **kwargs)
        
        self.color = color
        self.target_value = value
        self.current_value = 0
        
        self.configure(highlightbackground=Colors.BORDER, highlightthickness=1)
        
        # Layout
        content = tk.Frame(self, bg=Colors.BG_CARD)
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Icône (grand, à gauche)
        icon_label = tk.Label(content, text=icon, font=("Segoe UI Emoji", 32),
                             bg=Colors.BG_CARD, fg=color)
        icon_label.pack(side=tk.LEFT, padx=(0, 15))
        
        # Texte (à droite)
        text_frame = tk.Frame(content, bg=Colors.BG_CARD)
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.value_label = tk.Label(text_frame, text="0", 
                                   font=("Segoe UI", 28, "bold"),
                                   bg=Colors.BG_CARD, fg=Colors.TEXT_PRIMARY)
        self.value_label.pack(anchor=tk.W)
        
        title_label = tk.Label(text_frame, text=title,
                              font=("Segoe UI", 10),
                              bg=Colors.BG_CARD, fg=Colors.TEXT_MUTED)
        title_label.pack(anchor=tk.W)
        
        # Barre de progression décorative
        self.progress_frame = tk.Frame(self, bg=Colors.BORDER, height=3)
        self.progress_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.progress_bar = tk.Frame(self.progress_frame, bg=color, height=3, width=0)
        self.progress_bar.pack(side=tk.LEFT)
        
        # Hover effect
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
    
    def animate_value(self, final_value):
        """Anime le compteur de 0 à la valeur finale"""
        self.target_value = final_value
        self.current_value = 0
        self._animate_step()
    
    def _animate_step(self):
        if self.current_value < self.target_value:
            increment = max(1, (self.target_value - self.current_value) // 10)
            self.current_value = min(self.current_value + increment, self.target_value)
            
            if isinstance(self.target_value, float):
                self.value_label.config(text=f"{self.current_value:.2f}€")
            else:
                self.value_label.config(text=str(int(self.current_value)))
            
            self.after(30, self._animate_step)
        else:
            if isinstance(self.target_value, float):
                self.value_label.config(text=f"{self.target_value:.2f}€")
            else:
                self.value_label.config(text=str(int(self.target_value)))
    
    def set_progress(self, percent):
        """Définit la progression (0-100)"""
        width = int(self.winfo_width() * percent / 100)
        self.progress_bar.configure(width=max(0, width))
    
    def on_enter(self, event):
        self.configure(highlightbackground=self.color)
    
    def on_leave(self, event):
        self.configure(highlightbackground=Colors.BORDER)


class ModernScrolledText(tk.Frame):
    """Zone de texte avec scrollbar moderne"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=Colors.BG_DARKER)
        
        # Canvas pour le fond
        self.canvas = tk.Canvas(self, bg=Colors.BG_DARKER, highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar custom
        self.scrollbar = tk.Frame(self, bg=Colors.BG_CARD, width=8)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.scroll_thumb = tk.Frame(self.scrollbar, bg=Colors.PRIMARY, width=6)
        self.scroll_thumb.place(x=1, y=0, width=6, height=50)
        
        # Text widget
        self.text = tk.Text(self.canvas, 
                           bg=Colors.BG_DARKER,
                           fg=Colors.TEXT_PRIMARY,
                           font=("JetBrains Mono", 10),
                           insertbackground=Colors.PRIMARY,
                           selectbackground=Colors.PRIMARY,
                           selectforeground=Colors.TEXT_PRIMARY,
                           relief=tk.FLAT,
                           padx=15, pady=15,
                           wrap=tk.WORD,
                           highlightthickness=0,
                           **kwargs)
        self.text.pack(fill=tk.BOTH, expand=True)
        
        # Bind scroll
        self.text.bind("<MouseWheel>", self.on_scroll)
        
        # Tags pour le styling
        self.text.tag_configure("title", font=("Segoe UI", 16, "bold"), foreground=Colors.PRIMARY)
        self.text.tag_configure("subtitle", font=("Segoe UI", 12, "bold"), foreground=Colors.SECONDARY)
        self.text.tag_configure("success", foreground=Colors.SUCCESS)
        self.text.tag_configure("warning", foreground=Colors.WARNING)
        self.text.tag_configure("accent", foreground=Colors.ACCENT)
        self.text.tag_configure("muted", foreground=Colors.TEXT_MUTED)
        self.text.tag_configure("gold", foreground=Colors.GOLD)
        self.text.tag_configure("number", font=("JetBrains Mono", 11, "bold"), foreground=Colors.SECONDARY_LIGHT)
    
    def on_scroll(self, event):
        self.text.yview_scroll(-1 * (event.delta // 120), "units")
        self.update_scrollbar()
    
    def update_scrollbar(self):
        # Mettre à jour la position du thumb
        first, last = self.text.yview()
        height = self.scrollbar.winfo_height()
        thumb_height = max(30, int((last - first) * height))
        thumb_y = int(first * height)
        self.scroll_thumb.place(y=thumb_y, height=thumb_height)
    
    def insert(self, index, text, tags=None):
        self.text.insert(index, text, tags)
    
    def delete(self, start, end):
        self.text.delete(start, end)
    
    def get(self, start, end):
        return self.text.get(start, end)


class AnimatedLogo(tk.Canvas):
    """Logo animé avec effet de pulsation"""
    
    def __init__(self, parent, size=60, **kwargs):
        super().__init__(parent, width=size, height=size, 
                        bg=Colors.BG_DARK, highlightthickness=0, **kwargs)
        
        self.size = size
        self.pulse = 0
        self.animate()
    
    def animate(self):
        self.delete("all")
        
        # Cercles pulsants
        for i in range(3):
            offset = (self.pulse + i * 30) % 90
            alpha = 1 - offset / 90
            radius = self.size//4 + offset//3
            color = self._alpha_color(Colors.PRIMARY, alpha)
            
            self.create_oval(
                self.size//2 - radius, self.size//2 - radius,
                self.size//2 + radius, self.size//2 + radius,
                outline=color, width=2
            )
        
        # Centre - ticket emoji
        self.create_text(self.size//2, self.size//2, text="🎫",
                        font=("Segoe UI Emoji", self.size//3))
        
        self.pulse = (self.pulse + 2) % 90
        self.after(50, self.animate)
    
    def _alpha_color(self, color, alpha):
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        bg_r, bg_g, bg_b = int(Colors.BG_DARK[1:3], 16), int(Colors.BG_DARK[3:5], 16), int(Colors.BG_DARK[5:7], 16)
        
        r = int(bg_r + (r - bg_r) * alpha)
        g = int(bg_g + (g - bg_g) * alpha)
        b = int(bg_b + (b - bg_b) * alpha)
        
        return f"#{r:02x}{g:02x}{b:02x}"


class ParticleBackground(tk.Canvas):
    """Fond avec particules animées"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=Colors.BG_DARK, highlightthickness=0, **kwargs)
        
        self.particles = []
        self.init_particles(50)
        self.animate()
    
    def init_particles(self, count):
        import random
        for _ in range(count):
            self.particles.append({
                'x': random.randint(0, 1000),
                'y': random.randint(0, 800),
                'vx': random.uniform(-0.3, 0.3),
                'vy': random.uniform(-0.3, 0.3),
                'size': random.randint(1, 3),
                'color': random.choice([Colors.PRIMARY, Colors.SECONDARY, Colors.ACCENT])
            })
    
    def animate(self):
        self.delete("all")
        
        width = self.winfo_width()
        height = self.winfo_height()
        
        for p in self.particles:
            # Mouvement
            p['x'] += p['vx']
            p['y'] += p['vy']
            
            # Rebond sur les bords
            if p['x'] < 0 or p['x'] > width:
                p['vx'] *= -1
            if p['y'] < 0 or p['y'] > height:
                p['vy'] *= -1
            
            # Dessiner la particule
            self.create_oval(
                p['x'] - p['size'], p['y'] - p['size'],
                p['x'] + p['size'], p['y'] + p['size'],
                fill=p['color'], outline=""
            )
        
        # Lignes entre particules proches
        for i, p1 in enumerate(self.particles):
            for p2 in self.particles[i+1:]:
                dist = ((p1['x']-p2['x'])**2 + (p1['y']-p2['y'])**2)**0.5
                if dist < 100:
                    alpha = 1 - dist/100
                    color = self._alpha_color(Colors.BORDER, alpha * 0.3)
                    self.create_line(p1['x'], p1['y'], p2['x'], p2['y'], fill=color)
        
        self.after(50, self.animate)
    
    def _alpha_color(self, color, alpha):
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        bg_r, bg_g, bg_b = int(Colors.BG_DARK[1:3], 16), int(Colors.BG_DARK[3:5], 16), int(Colors.BG_DARK[5:7], 16)
        
        r = int(bg_r + (r - bg_r) * alpha)
        g = int(bg_g + (g - bg_g) * alpha)
        b = int(bg_b + (b - bg_b) * alpha)
        
        return f"#{r:02x}{g:02x}{b:02x}"


# ============================================
# 🎫 APPLICATION PRINCIPALE
# ============================================
class BilletterieApp:
    """Application principale de gestion de billetterie - PREMIUM EDITION"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🎫 BILLETTERIE PRO | Ridwan & Sébastien")
        
        # On récupère la taille de l'écran pour s'adapter
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        # Taille de la fenêtre = 85% de l'écran
        win_width = min(1400, int(screen_width * 0.85))
        win_height = min(900, int(screen_height * 0.85))
        
        # Position centrée
        x = (screen_width - win_width) // 2
        y = (screen_height - win_height) // 2
        
        self.root.geometry(f"{win_width}x{win_height}+{x}+{y}")
        self.root.configure(bg=Colors.BG_DARK)
        self.root.minsize(800, 600)
        
        # Service métier
        self.service = BilletterieService()
        
        # Construction de l'interface
        self.create_ui()
        
        # Animation d'entrée
        self.root.attributes('-alpha', 0)
        self.fade_in()
        
        # Gestion de la fermeture
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def fade_in(self):
        """Animation de fade in au démarrage"""
        alpha = self.root.attributes('-alpha')
        if alpha < 1:
            self.root.attributes('-alpha', alpha + 0.05)
            self.root.after(20, self.fade_in)
    
    def create_ui(self):
        """Crée l'interface utilisateur"""
        # Container principal
        self.main_container = tk.Frame(self.root, bg=Colors.BG_DARK)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self.create_header()
        
        # Content area
        content = tk.Frame(self.main_container, bg=Colors.BG_DARK)
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Sidebar gauche
        self.create_sidebar(content)
        
        # Zone principale
        self.create_main_area(content)
        
        # Footer/Status bar
        self.create_footer()
    
    def create_header(self):
        """Header avec logo animé et titre"""
        header = tk.Frame(self.main_container, bg=Colors.BG_DARKER, height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Container interne
        inner = tk.Frame(header, bg=Colors.BG_DARKER)
        inner.pack(fill=tk.BOTH, expand=True, padx=30)
        
        # Logo animé
        self.logo = AnimatedLogo(inner, size=50)
        self.logo.pack(side=tk.LEFT, pady=15)
        
        # Titre
        title_frame = tk.Frame(inner, bg=Colors.BG_DARKER)
        title_frame.pack(side=tk.LEFT, padx=15)
        
        title = tk.Label(title_frame, text="BILLETTERIE PRO",
                        font=("Segoe UI", 22, "bold"),
                        bg=Colors.BG_DARKER, fg=Colors.TEXT_PRIMARY)
        title.pack(anchor=tk.W)
        
        subtitle = tk.Label(title_frame, text="Gestion de billetterie locale • Ridwan & Sébastien",
                           font=("Segoe UI", 10),
                           bg=Colors.BG_DARKER, fg=Colors.TEXT_MUTED)
        subtitle.pack(anchor=tk.W)
        
        # Stats rapides à droite
        stats_frame = tk.Frame(inner, bg=Colors.BG_DARKER)
        stats_frame.pack(side=tk.RIGHT, pady=15)
        
        # Mini stats
        self.create_mini_stat(stats_frame, "💰", "CA Total", Colors.SUCCESS)
        self.create_mini_stat(stats_frame, "🎫", "Billets", Colors.PRIMARY)
        self.create_mini_stat(stats_frame, "🎭", "Events", Colors.SECONDARY)
    
    def create_mini_stat(self, parent, icon, label, color):
        """Crée une mini stat dans le header"""
        frame = tk.Frame(parent, bg=Colors.BG_DARKER)
        frame.pack(side=tk.LEFT, padx=15)
        
        tk.Label(frame, text=icon, font=("Segoe UI Emoji", 16),
                bg=Colors.BG_DARKER, fg=color).pack(side=tk.LEFT)
        
        tk.Label(frame, text=label, font=("Segoe UI", 9),
                bg=Colors.BG_DARKER, fg=Colors.TEXT_MUTED).pack(side=tk.LEFT, padx=(5, 0))
    
    def create_sidebar(self, parent):
        """Sidebar avec les boutons d'action - responsive avec scrollbar"""
        # Frame conteneur pour la sidebar
        sidebar_container = tk.Frame(parent, bg=Colors.BG_CARD)
        sidebar_container.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        
        # Canvas avec scrollbar pour les petits écrans
        canvas = tk.Canvas(sidebar_container, bg=Colors.BG_CARD, 
                          highlightthickness=0, width=250)
        scrollbar = tk.Scrollbar(sidebar_container, orient="vertical", 
                                command=canvas.yview)
        
        button_frame = tk.Frame(canvas, bg=Colors.BG_CARD)
        
        # Configuration du scroll
        button_frame.bind("<Configure>", 
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=button_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Scroll avec la molette
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # ═══════════════════════════════════════
        # SECTION: GESTION
        # ═══════════════════════════════════════
        self.create_section_header(button_frame, "📋 GESTION", Colors.PRIMARY)
        
        GlowButton(button_frame, "➕  Ajouter Vente", 
                  self.ajouter_vente, Colors.SUCCESS).pack(pady=5, padx=15)
        
        GlowButton(button_frame, "�️  Supprimer Vente", 
                  self.supprimer_vente, Colors.ACCENT).pack(pady=5, padx=15)
        
        GlowButton(button_frame, "📜  Lister Ventes", 
                  self.lister_ventes, Colors.PRIMARY).pack(pady=5, padx=15)
        
        GlowButton(button_frame, "🔄  Rafraîchir", 
                  self.rafraichir_affichage, Colors.SECONDARY).pack(pady=5, padx=15)
        
        GlowButton(button_frame, "🎭  Événements", 
                  self.lister_evenements, Colors.SECONDARY).pack(pady=5, padx=15)
        
        GlowButton(button_frame, "👥  Acheteurs", 
                  self.lister_acheteurs, Colors.PRIMARY_LIGHT).pack(pady=5, padx=15)
        
        # ═══════════════════════════════════════
        # SECTION: ANALYTICS
        # ═══════════════════════════════════════
        self.create_section_header(button_frame, "📊 ANALYTICS", Colors.SECONDARY)
        
        GlowButton(button_frame, "💰  Chiffre d'Affaires", 
                  self.calculer_ca, Colors.SUCCESS).pack(pady=5, padx=15)
        
        GlowButton(button_frame, "🏆  Top Billets", 
                  self.afficher_top_billets, Colors.GOLD).pack(pady=5, padx=15)
        
        GlowButton(button_frame, "📈  Taux Remplissage", 
                  self.afficher_taux_remplissage, Colors.SECONDARY).pack(pady=5, padx=15)
        
        GlowButton(button_frame, "🎯  CA / Événement", 
                  self.afficher_ca_evenement, Colors.PRIMARY).pack(pady=5, padx=15)
        
        GlowButton(button_frame, "🔬  Dashboard Avancé", 
                  self.afficher_indicateurs_avances, Colors.ACCENT).pack(pady=5, padx=15)
        
        # ═══════════════════════════════════════
        # SECTION: SYSTÈME
        # ═══════════════════════════════════════
        self.create_section_header(button_frame, "⚙️ SYSTÈME", Colors.TEXT_MUTED)
        
        GlowButton(button_frame, "🔄  Réinitialiser DB", 
                  self.reinitialiser_base, Colors.ACCENT).pack(pady=5, padx=15)
        
        # Spacer
        tk.Frame(button_frame, bg=Colors.BG_CARD, height=20).pack()
    
    def create_section_header(self, parent, text, color):
        """Crée un header de section stylé"""
        frame = tk.Frame(parent, bg=Colors.BG_CARD)
        frame.pack(fill=tk.X, padx=15, pady=(20, 10))
        
        tk.Label(frame, text=text, font=("Segoe UI", 11, "bold"),
                bg=Colors.BG_CARD, fg=color).pack(side=tk.LEFT)
        
        # Ligne décorative
        line = tk.Frame(frame, bg=color, height=1)
        line.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0), pady=8)
    
    def create_main_area(self, parent):
        """Zone principale avec stats et résultats"""
        main = tk.Frame(parent, bg=Colors.BG_DARK)
        main.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # ═══════════════════════════════════════
        # STATS CARDS (en haut)
        # ═══════════════════════════════════════
        stats_row = tk.Frame(main, bg=Colors.BG_DARK)
        stats_row.pack(fill=tk.X, pady=(0, 20))
        
        # Configurer la grille
        for i in range(4):
            stats_row.columnconfigure(i, weight=1)
        
        # Stat Cards
        self.stat_ca = StatCard(stats_row, "Chiffre d'Affaires", 0, "💰", Colors.SUCCESS)
        self.stat_ca.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        
        self.stat_billets = StatCard(stats_row, "Billets Vendus", 0, "🎫", Colors.PRIMARY)
        self.stat_billets.grid(row=0, column=1, padx=5, sticky="nsew")
        
        self.stat_events = StatCard(stats_row, "Événements", 0, "🎭", Colors.SECONDARY)
        self.stat_events.grid(row=0, column=2, padx=5, sticky="nsew")
        
        self.stat_clients = StatCard(stats_row, "Clients", 0, "👥", Colors.ACCENT)
        self.stat_clients.grid(row=0, column=3, padx=(10, 0), sticky="nsew")
        
        # Charger les stats initiales
        self.root.after(500, self.load_initial_stats)
        
        # ═══════════════════════════════════════
        # ZONE DE RÉSULTATS
        # ═══════════════════════════════════════
        result_card = NeonCard(main, "RÉSULTATS", "📋", Colors.PRIMARY)
        result_card.pack(fill=tk.BOTH, expand=True)
        
        self.result_text = ModernScrolledText(result_card.content)
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # Message de bienvenue
        self.show_welcome()
    
    def create_footer(self):
        """Footer avec barre de statut"""
        footer = tk.Frame(self.main_container, bg=Colors.BG_DARKER, height=35)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        footer.pack_propagate(False)
        
        inner = tk.Frame(footer, bg=Colors.BG_DARKER)
        inner.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # Status indicator
        self.status_dot = tk.Label(inner, text="●", font=("Segoe UI", 10),
                                   bg=Colors.BG_DARKER, fg=Colors.SUCCESS)
        self.status_dot.pack(side=tk.LEFT, pady=8)
        
        self.status_label = tk.Label(inner, text="Système opérationnel",
                                    font=("Segoe UI", 9),
                                    bg=Colors.BG_DARKER, fg=Colors.TEXT_MUTED)
        self.status_label.pack(side=tk.LEFT, padx=(5, 0), pady=8)
        
        # Version
        version = tk.Label(inner, text="v2.0 Premium Edition",
                          font=("Segoe UI", 9),
                          bg=Colors.BG_DARKER, fg=Colors.TEXT_MUTED)
        version.pack(side=tk.RIGHT, pady=8)
        
        # Séparateur
        tk.Label(inner, text="│", bg=Colors.BG_DARKER, 
                fg=Colors.BORDER).pack(side=tk.RIGHT, padx=10, pady=8)
        
        # Datetime (simulé)
        import datetime
        now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        tk.Label(inner, text=now, font=("Segoe UI", 9),
                bg=Colors.BG_DARKER, fg=Colors.TEXT_MUTED).pack(side=tk.RIGHT, pady=8)
    
    def set_status(self, message, status="success"):
        """Met à jour le statut"""
        colors = {
            "success": Colors.SUCCESS,
            "warning": Colors.WARNING,
            "error": Colors.ACCENT,
            "info": Colors.PRIMARY
        }
        self.status_dot.config(fg=colors.get(status, Colors.SUCCESS))
        self.status_label.config(text=message)
    
    def load_initial_stats(self):
        """Charge et anime les statistiques initiales"""
        try:
            stats = self.service.calculer_chiffre_affaires_total()
            events = self.service.lister_evenements()
            clients = self.service.lister_acheteurs()
            
            self.stat_ca.animate_value(stats['chiffre_affaires_total'])
            self.stat_billets.animate_value(stats['quantite_totale_vendue'])
            self.stat_events.animate_value(len(events))
            self.stat_clients.animate_value(len(clients))
            
            # Progress bars
            self.root.after(1000, lambda: self.stat_ca.set_progress(75))
            self.root.after(1200, lambda: self.stat_billets.set_progress(60))
            self.root.after(1400, lambda: self.stat_events.set_progress(100))
            self.root.after(1600, lambda: self.stat_clients.set_progress(80))
        except:
            pass
    
    def show_welcome(self):
        """Affiche le message de bienvenue"""
        self.result_text.delete("1.0", tk.END)
        
        self.result_text.insert(tk.END, "Bienvenue dans BILLETTERIE PRO\n", "title")
        self.result_text.insert(tk.END, "━" * 50 + "\n\n", "muted")
        
        self.result_text.insert(tk.END, "🚀 ", "")
        self.result_text.insert(tk.END, "Application prête à l'emploi\n\n", "success")
        
        self.result_text.insert(tk.END, "Utilisez les boutons à gauche pour naviguer.\n\n", "")
        
        self.result_text.insert(tk.END, "ÉQUIVALENCES API\n", "subtitle")
        self.result_text.insert(tk.END, "─" * 30 + "\n", "muted")
        
        apis = [
            ("➕ Ajouter Vente", "POST /vente"),
            ("📜 Lister Ventes", "GET /ventes"),
            ("💰 Calcul CA", "GET /stats/ca"),
            ("🏆 Top Billets", "GET /stats/top"),
        ]
        
        for btn, api in apis:
            self.result_text.insert(tk.END, f"  {btn}  ", "")
            self.result_text.insert(tk.END, "→  ", "muted")
            self.result_text.insert(tk.END, f"{api}\n", "accent")
    
    def afficher_message(self, title, content, title_color="title"):
        """Affiche un message formaté"""
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, f"{title}\n", title_color)
        self.result_text.insert(tk.END, "━" * 50 + "\n\n", "muted")
        self.result_text.insert(tk.END, content)
    
    # ============================================
    # 🎯 ACTIONS (même logique, juste affichage amélioré)
    # ============================================
    
    def rafraichir_affichage(self):
        """Rafraîchit les stats et la liste des ventes"""
        self.set_status("Rafraîchissement...", "info")
        self.load_initial_stats()
        self.lister_ventes()
        self.set_status("Affichage rafraîchi!", "success")
    
    def supprimer_vente(self):
        """Supprime une vente après confirmation"""
        self.set_status("Suppression d'une vente...", "info")
        
        # On demande l'ID de la vente à supprimer
        id_str = simpledialog.askstring(
            "Supprimer une vente", 
            "Entrez l'ID de la vente à supprimer:",
            parent=self.root
        )
        
        if id_str is None:
            self.set_status("Opération annulée", "warning")
            return
        
        try:
            id_vente = int(id_str)
        except ValueError:
            messagebox.showerror("Erreur", "L'ID doit être un nombre entier")
            return
        
        # Confirmation avant suppression
        confirm = messagebox.askyesno(
            "Confirmer la suppression",
            f"Voulez-vous vraiment supprimer la vente #{id_vente} ?\n\n(Les billets seront remis en stock)"
        )
        
        if confirm:
            result = self.service.annuler_vente(id_vente)
            
            if result['success']:
                self.set_status(f"Vente #{id_vente} supprimée!", "success")
                self.load_initial_stats()
                
                self.result_text.delete("1.0", tk.END)
                self.result_text.insert(tk.END, "🗑️ VENTE SUPPRIMÉE\n", "title")
                self.result_text.insert(tk.END, "━" * 50 + "\n\n", "muted")
                self.result_text.insert(tk.END, f"La vente ", "")
                self.result_text.insert(tk.END, f"#{id_vente}", "number")
                self.result_text.insert(tk.END, f" a été supprimée.\n\n", "")
                self.result_text.insert(tk.END, "Les billets ont été remis en stock.", "success")
            else:
                self.set_status("Erreur lors de la suppression", "error")
                messagebox.showerror("Erreur", result['error'])
        else:
            self.set_status("Suppression annulée", "warning")
    
    def ajouter_vente(self):
        """Ajoute une vente"""
        self.set_status("Ajout d'une vente...", "info")
        
        dialog = ModernVenteDialog(self.root, self.service)
        if dialog.result:
            result = self.service.effectuer_vente(
                dialog.result['id_acheteur'],
                dialog.result['id_type_billet'],
                dialog.result['quantite']
            )
            
            if result['success']:
                self.set_status("Vente effectuée avec succès!", "success")
                self.load_initial_stats()
                
                self.result_text.delete("1.0", tk.END)
                self.result_text.insert(tk.END, "✅ VENTE EFFECTUÉE\n", "title")
                self.result_text.insert(tk.END, "━" * 50 + "\n\n", "muted")
                self.result_text.insert(tk.END, f"ID Vente: ", "")
                self.result_text.insert(tk.END, f"#{result['id_vente']}\n", "number")
                self.result_text.insert(tk.END, f"Montant: ", "")
                self.result_text.insert(tk.END, f"{result['montant_total']:.2f}€\n", "success")
            else:
                self.set_status("Erreur lors de la vente", "error")
                messagebox.showerror("Erreur", result['error'])
        else:
            self.set_status("Opération annulée", "warning")
    
    def lister_ventes(self):
        """Liste les ventes"""
        self.set_status("Chargement des ventes...", "info")
        
        ventes = self.service.lister_ventes()
        
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, "📜 HISTORIQUE DES VENTES\n", "title")
        self.result_text.insert(tk.END, "━" * 50 + "\n\n", "muted")
        
        if not ventes:
            self.result_text.insert(tk.END, "Aucune vente enregistrée.\n", "warning")
        else:
            for v in ventes:
                self.result_text.insert(tk.END, f"🎫 Vente ", "")
                self.result_text.insert(tk.END, f"#{v['id_vente']}\n", "number")
                self.result_text.insert(tk.END, f"   Event: {v['evenement']}\n", "")
                self.result_text.insert(tk.END, f"   Type: ", "muted")
                self.result_text.insert(tk.END, f"{v['type_billet']} ", "")
                self.result_text.insert(tk.END, f"({v['prix_unitaire']:.2f}€)\n", "number")
                self.result_text.insert(tk.END, f"   Client: {v['acheteur']}\n", "")
                self.result_text.insert(tk.END, f"   Qté: ", "muted")
                self.result_text.insert(tk.END, f"{v['quantite']}", "number")
                self.result_text.insert(tk.END, f" │ Total: ", "muted")
                self.result_text.insert(tk.END, f"{v['montant_total']:.2f}€\n", "success")
                self.result_text.insert(tk.END, f"   📅 {v['date_vente']}\n", "muted")
                self.result_text.insert(tk.END, "   ─" * 15 + "\n", "muted")
            
            self.result_text.insert(tk.END, f"\n📊 Total: ", "")
            self.result_text.insert(tk.END, f"{len(ventes)} vente(s)\n", "number")
        
        self.set_status(f"{len(ventes)} vente(s) trouvée(s)", "success")
    
    def lister_evenements(self):
        """Liste les événements"""
        self.set_status("Chargement des événements...", "info")
        
        evenements = self.service.lister_evenements()
        
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, "🎭 ÉVÉNEMENTS\n", "title")
        self.result_text.insert(tk.END, "━" * 50 + "\n\n", "muted")
        
        if not evenements:
            self.result_text.insert(tk.END, "Aucun événement.\n", "warning")
        else:
            for e in evenements:
                cat_icons = {"concert": "🎸", "conference": "🎤", "spectacle": "🎪"}
                icon = cat_icons.get(e['categorie'], "🎭")
                
                self.result_text.insert(tk.END, f"{icon} ", "")
                self.result_text.insert(tk.END, f"{e['nom']}\n", "subtitle")
                self.result_text.insert(tk.END, f"   📅 {e['date_evenement']} à {e['heure_debut']}\n", "")
                self.result_text.insert(tk.END, f"   📍 {e['lieu']}\n", "muted")
                self.result_text.insert(tk.END, f"   👥 Capacité: ", "muted")
                self.result_text.insert(tk.END, f"{e['capacite_max']} places\n", "number")
                self.result_text.insert(tk.END, f"   🏷️ {e['categorie'].upper()}\n", "accent")
                self.result_text.insert(tk.END, "   ─" * 15 + "\n", "muted")
        
        self.set_status(f"{len(evenements)} événement(s)", "success")
    
    def lister_acheteurs(self):
        """Liste les acheteurs"""
        self.set_status("Chargement...", "info")
        
        acheteurs = self.service.lister_acheteurs()
        
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, "👥 CLIENTS\n", "title")
        self.result_text.insert(tk.END, "━" * 50 + "\n\n", "muted")
        
        for a in acheteurs:
            self.result_text.insert(tk.END, f"👤 ", "")
            self.result_text.insert(tk.END, f"{a['prenom']} {a['nom']}\n", "subtitle")
            self.result_text.insert(tk.END, f"   📧 {a['email']}\n", "")
            self.result_text.insert(tk.END, f"   📱 {a['telephone'] or 'Non renseigné'}\n", "muted")
            self.result_text.insert(tk.END, f"   📅 Inscrit le {a['date_inscription']}\n", "muted")
            self.result_text.insert(tk.END, "   ─" * 15 + "\n", "muted")
        
        self.set_status(f"{len(acheteurs)} client(s)", "success")
    
    def calculer_ca(self):
        """Affiche le CA"""
        self.set_status("Calcul en cours...", "info")
        
        stats = self.service.calculer_chiffre_affaires_total()
        
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, "💰 CHIFFRE D'AFFAIRES\n", "title")
        self.result_text.insert(tk.END, "━" * 50 + "\n\n", "muted")
        
        self.result_text.insert(tk.END, "CA Total\n", "subtitle")
        self.result_text.insert(tk.END, f"  {stats['chiffre_affaires_total']:.2f} €\n\n", "success")
        
        self.result_text.insert(tk.END, "Billets vendus\n", "subtitle")
        self.result_text.insert(tk.END, f"  {stats['quantite_totale_vendue']} unités\n\n", "number")
        
        self.result_text.insert(tk.END, "Panier moyen\n", "subtitle")
        self.result_text.insert(tk.END, f"  {stats['panier_moyen']:.2f} €\n", "accent")
        
        self.set_status("CA calculé", "success")
    
    def afficher_top_billets(self):
        """Top des billets"""
        self.set_status("Analyse...", "info")
        
        top = self.service.obtenir_top_billets()
        
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, "🏆 CLASSEMENT DES VENTES\n", "title")
        self.result_text.insert(tk.END, "━" * 50 + "\n\n", "muted")
        
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
        
        for i, b in enumerate(top[:5]):
            medal = medals[i] if i < len(medals) else f"{i+1}."
            self.result_text.insert(tk.END, f"{medal} ", "")
            self.result_text.insert(tk.END, f"{b['nom_type']}\n", "subtitle")
            self.result_text.insert(tk.END, f"   📍 {b['evenement']}\n", "muted")
            self.result_text.insert(tk.END, f"   🎫 Vendus: ", "")
            self.result_text.insert(tk.END, f"{b['total_vendu']}\n", "number")
            self.result_text.insert(tk.END, f"   💰 CA: ", "")
            self.result_text.insert(tk.END, f"{b['ca_type']:.2f}€\n", "success")
            self.result_text.insert(tk.END, "\n", "")
        
        self.set_status("Classement affiché", "success")
    
    def afficher_taux_remplissage(self):
        """Taux de remplissage"""
        self.set_status("Calcul...", "info")
        
        taux = self.service.calculer_taux_remplissage()
        
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, "📈 TAUX DE REMPLISSAGE\n", "title")
        self.result_text.insert(tk.END, "━" * 50 + "\n\n", "muted")
        
        for t in taux:
            self.result_text.insert(tk.END, f"🎪 {t['evenement']}\n", "subtitle")
            
            # Barre de progression ASCII
            filled = int(t['taux_remplissage'] / 5)
            bar = "█" * filled + "░" * (20 - filled)
            
            color = "success" if t['taux_remplissage'] >= 70 else ("warning" if t['taux_remplissage'] >= 40 else "accent")
            
            self.result_text.insert(tk.END, f"   [{bar}] ", color)
            self.result_text.insert(tk.END, f"{t['taux_remplissage']}%\n", "number")
            self.result_text.insert(tk.END, f"   {t['billets_vendus']}/{t['capacite_max']} places\n\n", "muted")
        
        self.set_status("Analyse terminée", "success")
    
    def afficher_ca_evenement(self):
        """CA par événement"""
        self.set_status("Analyse...", "info")
        
        ca = self.service.calculer_ca_par_evenement()
        
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, "🎯 CA PAR ÉVÉNEMENT\n", "title")
        self.result_text.insert(tk.END, "━" * 50 + "\n\n", "muted")
        
        for e in ca:
            self.result_text.insert(tk.END, f"🎭 {e['evenement']}\n", "subtitle")
            self.result_text.insert(tk.END, f"   📅 {e['date_evenement']} • ", "muted")
            self.result_text.insert(tk.END, f"{e['categorie'].upper()}\n", "accent")
            self.result_text.insert(tk.END, f"   💰 CA: ", "")
            self.result_text.insert(tk.END, f"{e['chiffre_affaires']:.2f}€\n", "success")
            self.result_text.insert(tk.END, f"   🎫 Billets: ", "")
            self.result_text.insert(tk.END, f"{e['billets_vendus']}\n\n", "number")
        
        self.set_status("Analyse terminée", "success")
    
    def afficher_indicateurs_avances(self):
        """Dashboard avancé"""
        self.set_status("Génération du dashboard...", "info")
        
        ind = self.service.calculer_indicateurs_avances()
        
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, "🔬 DASHBOARD AVANCÉ\n", "title")
        self.result_text.insert(tk.END, "━" * 50 + "\n\n", "muted")
        
        metrics = [
            ("💰 CA Total", f"{ind['chiffre_affaires_total']:.2f}€", "success"),
            ("🎫 Billets vendus", str(ind['quantite_totale']), "number"),
            ("💵 Prix moyen/billet", f"{ind['prix_moyen_billet']:.2f}€", "accent"),
            ("📊 CA moyen/event", f"{ind['ca_moyen_par_evenement']:.2f}€", "number"),
            ("📈 Remplissage moyen", f"{ind['taux_remplissage_moyen']:.2f}%", "warning"),
            ("🏆 Top événement", ind['evenement_top'], "gold"),
        ]
        
        for label, value, tag in metrics:
            self.result_text.insert(tk.END, f"{label}\n", "subtitle")
            self.result_text.insert(tk.END, f"  ► ", "muted")
            self.result_text.insert(tk.END, f"{value}\n\n", tag)
        
        self.result_text.insert(tk.END, "─" * 40 + "\n", "muted")
        self.result_text.insert(tk.END, f"📅 Généré le {ind['date_analyse']}\n", "muted")
        
        self.set_status("Dashboard généré", "success")
    
    def reinitialiser_base(self):
        """Réinitialise la base"""
        if messagebox.askyesno("⚠️ Confirmation",
                              "Réinitialiser la base de données?\nToutes les données seront perdues!"):
            if init_database():
                self.set_status("Base réinitialisée", "success")
                self.load_initial_stats()
                self.show_welcome()
                messagebox.showinfo("✅ Succès", "Base de données réinitialisée!")
            else:
                self.set_status("Erreur", "error")
    
    def on_closing(self):
        """Fermeture propre"""
        self.service.fermer_connexion()
        self.root.destroy()


# ============================================
# 🎨 DIALOGUE MODERNE POUR VENTE
# ============================================
class ModernVenteDialog(tk.Toplevel):
    """Dialogue moderne pour ajouter une vente"""
    
    def __init__(self, parent, service):
        super().__init__(parent)
        
        self.service = service
        self.result = None
        
        # Configuration de la fenêtre
        self.title("➕ Nouvelle Vente")
        self.configure(bg=Colors.BG_DARK)
        
        # Taille adaptée à l'écran
        screen_w = parent.winfo_screenwidth()
        screen_h = parent.winfo_screenheight()
        dialog_w = min(450, int(screen_w * 0.35))
        dialog_h = min(450, int(screen_h * 0.5))
        x = (screen_w - dialog_w) // 2
        y = (screen_h - dialog_h) // 2
        self.geometry(f"{dialog_w}x{dialog_h}+{x}+{y}")
        self.resizable(True, True)
        self.minsize(350, 380)
        
        # Centrer la fenêtre
        self.transient(parent)
        self.grab_set()
        
        # Contenu
        self.create_content()
        
        # Attendre la fermeture
        self.wait_window()
    
    def create_content(self):
        # Header
        header = tk.Frame(self, bg=Colors.PRIMARY, height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="➕ NOUVELLE VENTE",
                font=("Segoe UI", 14, "bold"),
                bg=Colors.PRIMARY, fg=Colors.TEXT_PRIMARY).pack(pady=18)
        
        # Form
        form = tk.Frame(self, bg=Colors.BG_DARK)
        form.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # ID Acheteur
        tk.Label(form, text="ID Acheteur", font=("Segoe UI", 10),
                bg=Colors.BG_DARK, fg=Colors.TEXT_SECONDARY).pack(anchor=tk.W)
        
        self.acheteur_entry = tk.Entry(form, font=("Segoe UI", 12),
                                       bg=Colors.BG_CARD, fg=Colors.TEXT_PRIMARY,
                                       insertbackground=Colors.PRIMARY,
                                       relief=tk.FLAT, highlightthickness=2,
                                       highlightbackground=Colors.BORDER,
                                       highlightcolor=Colors.PRIMARY)
        self.acheteur_entry.pack(fill=tk.X, pady=(5, 15), ipady=8)
        
        # ID Type Billet
        tk.Label(form, text="ID Type Billet", font=("Segoe UI", 10),
                bg=Colors.BG_DARK, fg=Colors.TEXT_SECONDARY).pack(anchor=tk.W)
        
        self.billet_entry = tk.Entry(form, font=("Segoe UI", 12),
                                     bg=Colors.BG_CARD, fg=Colors.TEXT_PRIMARY,
                                     insertbackground=Colors.PRIMARY,
                                     relief=tk.FLAT, highlightthickness=2,
                                     highlightbackground=Colors.BORDER,
                                     highlightcolor=Colors.PRIMARY)
        self.billet_entry.pack(fill=tk.X, pady=(5, 15), ipady=8)
        
        # Quantité
        tk.Label(form, text="Quantité", font=("Segoe UI", 10),
                bg=Colors.BG_DARK, fg=Colors.TEXT_SECONDARY).pack(anchor=tk.W)
        
        self.quantite_entry = tk.Entry(form, font=("Segoe UI", 12),
                                       bg=Colors.BG_CARD, fg=Colors.TEXT_PRIMARY,
                                       insertbackground=Colors.PRIMARY,
                                       relief=tk.FLAT, highlightthickness=2,
                                       highlightbackground=Colors.BORDER,
                                       highlightcolor=Colors.PRIMARY)
        self.quantite_entry.pack(fill=tk.X, pady=(5, 15), ipady=8)
        self.quantite_entry.insert(0, "1")
        
        # Boutons
        btn_frame = tk.Frame(self, bg=Colors.BG_DARK)
        btn_frame.pack(fill=tk.X, padx=30, pady=(0, 20))
        
        cancel_btn = tk.Button(btn_frame, text="Annuler",
                              font=("Segoe UI", 10, "bold"),
                              bg=Colors.BG_CARD, fg=Colors.TEXT_SECONDARY,
                              activebackground=Colors.BG_CARD_HOVER,
                              relief=tk.FLAT, cursor="hand2",
                              command=self.destroy)
        cancel_btn.pack(side=tk.LEFT, ipadx=20, ipady=8)
        
        confirm_btn = tk.Button(btn_frame, text="✓ Confirmer",
                               font=("Segoe UI", 10, "bold"),
                               bg=Colors.SUCCESS, fg=Colors.TEXT_PRIMARY,
                               activebackground=Colors.SUCCESS_LIGHT,
                               relief=tk.FLAT, cursor="hand2",
                               command=self.confirm)
        confirm_btn.pack(side=tk.RIGHT, ipadx=20, ipady=8)
    
    def confirm(self):
        try:
            self.result = {
                'id_acheteur': int(self.acheteur_entry.get()),
                'id_type_billet': int(self.billet_entry.get()),
                'quantite': int(self.quantite_entry.get())
            }
            self.destroy()
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des valeurs numériques")


# ============================================
# 🚀 POINT D'ENTRÉE
# ============================================
def main():
    """Lance l'application"""
    from config import DATABASE_PATH
    
    if not os.path.exists(DATABASE_PATH):
        print("🔧 Initialisation de la base de données...")
        init_database()
    
    root = tk.Tk()
    
    # Style de la fenêtre
    root.configure(bg=Colors.BG_DARK)
    
    # Icône (optionnel)
    try:
        root.iconbitmap("icon.ico")
    except:
        pass
    
    app = BilletterieApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
