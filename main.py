import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import configparser
import threading

from common import get_base_dir
from pipeline_processa_csvs import main as pipeline_main
from gera_painel_turma import main as painel_main
from lista_pendencias_detalhada import main as lista_pendencias_main
from gera_aviso_alunos import main as gera_aviso_alunos_main


class Automatizador:
    def __init__(self):
        self.BASE_DIR = get_base_dir()
        self.log_file = self.BASE_DIR / "debug.log"
        
        # Cria pastas
        (self.BASE_DIR / "csv_brutos").mkdir(exist_ok=True)
        (self.BASE_DIR / "painel_turmas").mkdir(exist_ok=True)
        (self.BASE_DIR / "avisos_alunos").mkdir(exist_ok=True)
        
        self.root = tk.Tk()
        self.root.title("🤖 Automatizador Atividades v3.2")
        self.root.geometry("850x650")
        self.root.resizable(True, True)
        
        self.turmas = ['2DS', '3DS', '2ADME','2ADMD','3ADM']
        self.semana_padrao = 4
        self.load_config_safe()
        self.setup_ui()
    
    def load_config_safe(self):
        try:
            config_path = self.BASE_DIR / "config.ini"
            if config_path.exists():
                self.config = configparser.ConfigParser()
                self.config.read(config_path)
                
                self.turmas = [t.strip() for t in 
                              self.config.get('TURMAS', 'lista', fallback='2DS,3DS',).split(',')]
                
                self.semana_padrao = self.config.getint('SEMANAS', 'padrao', fallback=4)
                self.semana_padrao = max(1, min(self.semana_padrao, 20))
                
                print(f"✅ Config: {self.turmas}, semana {self.semana_padrao}")
            else:
                self.save_config()
        except Exception as e:
            print(f"⚠️ Config erro: {e}")
    
    def save_config(self):
        self.config = configparser.ConfigParser()
        self.config['TURMAS'] = {'lista': ','.join(self.turmas)}
        self.config['SEMANAS'] = {'padrao': str(self.semana_padrao)}
        with open(self.BASE_DIR / "config.ini", 'w') as f:
            self.config.write(f)
    
    def log(self, msg):
        timestamp = f"[{len(self.logs)}] {msg}"
        self.log_text.insert('end', timestamp + '\n')
        self.log_text.see('end')
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(timestamp + '\n')
    
    def setup_ui(self):
        # Título
        title = tk.Label(self.root, text="🤖 Automatizador Atividades v3.2", 
                        font=('Arial', 20, 'bold'), fg="#2E7D32")
        title.pack(pady=20)
        
        # Frame controles (ALINHADO)
        ctrl_frame = tk.Frame(self.root, relief='raised', bd=3, bg="#F0F8FF")
        ctrl_frame.pack(pady=15, padx=30, fill='x')
        
        # Turma
        tk.Label(ctrl_frame, text="👥 Turma:", font=('Arial', 13, 'bold'), 
                bg="#F0F8FF").grid(row=0, column=0, padx=25, pady=20, sticky='w')
        self.turma_var = tk.StringVar(value=self.turmas[0])
        turma_combo = ttk.Combobox(ctrl_frame, textvariable=self.turma_var,
                                  values=self.turmas, state="readonly",
                                  width=14, font=('Arial', 13))
        turma_combo.grid(row=0, column=1, padx=20, pady=20)
        
        # Semana LIVRE
        tk.Label(ctrl_frame, text="📅 Semana:", font=('Arial', 13, 'bold'), 
                bg="#F0F8FF").grid(row=0, column=2, padx=(30,20), pady=20, sticky='w')
        self.semana_entry = tk.Entry(ctrl_frame, width=8, font=('Arial', 15, 'bold'),
                                   justify='center', bg="#E8F4FD")
        self.semana_entry.insert(0, str(self.semana_padrao))
        self.semana_entry.grid(row=0, column=3, padx=15, pady=20)
        
        # Validação semana
        def validar_semana(P):
            if not P: return True
            try:
                n = int(P)
                return 1 <= n <= 20
            except:
                return False
        vcmd = (self.root.register(validar_semana), '%P')
        self.semana_entry.config(validate='key', validatecommand=vcmd)
        
        # Botão
        self.btn = tk.Button(ctrl_frame, text="🚀 EXECUTAR", 
                            command=self.start_execution,
                            bg="#4CAF50", fg="white", font=('Arial', 12, 'bold'),
                            width=16, height=2, relief='raised', bd=4)
        self.btn.grid(row=0, column=4, padx=(5,5), pady=10)
        
        # Status CSV
        self.status_label = tk.Label(self.root, text="📁 csv_brutos/: vazio", 
                                   font=('Arial', 12, 'bold'), fg="#D32F2F")
        self.status_label.pack(pady=15)
        
        # LOG
        log_frame = tk.Frame(self.root, relief='sunken', bd=2)
        log_frame.pack(fill='both', expand=True, padx=25, pady=15)
        
        tk.Label(log_frame, text="📋 LOG EXECUÇÃO (Ctrl+C copia) | debug.log salvo", 
                font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0,5))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=18, 
                                                 font=('Consolas', 11),
                                                 wrap=tk.WORD, bg="#FAFAFA")
        self.log_text.pack(fill='both', expand=True, padx=10, pady=5)
        self.log_text.bind('<Control-c>', lambda e: 'break')
        
        self.logs = []
        self.update_csv_status()
        self.log("✅ v3.2 carregado | Turmas: " + ", ".join(self.turmas))
        self.log("📁 Coloque CSVs em csv_brutos/ → selecione turma → 🚀")
    
    def update_csv_status(self):
        csv_brutos = self.BASE_DIR / "csv_brutos"
        arquivos = list(csv_brutos.glob("*.csv"))
        count = len(arquivos)
        status = f"📁 csv_brutos/: {count} arquivo(s)"
        color = "#4CAF50" if count >= 1 else "#D32F2F"
        self.status_label.config(text=status, fg=color)
    
    def reset_btn(self):
        self.btn.config(text="🚀 EXECUTAR", state='normal', bg="#4CAF50")
    
    def start_execution(self):
        if self.btn['text'] != "🚀 EXECUTAR":
            return
        threading.Thread(target=self.executar, daemon=True).start()
    
    def executar(self):
        self.btn.config(text="⏳ EXECUTANDO...", state='disabled', bg="#FF9800")
        
        turma = self.turma_var.get()
        semana_str = self.semana_entry.get()
        
        # Valida semana
        try:
            semana = int(semana_str)
            if not 1 <= semana <= 20:
                raise ValueError("1-20")
        except:
            messagebox.showerror("❌ Erro", "Semana: número 1-20!")
            self.reset_btn()
            return
        
        # ✅ VALIDA CSV TURMA
        csv_brutos = self.BASE_DIR / "csv_brutos"
        csvs_turma = [f for f in csv_brutos.glob("*.csv") 
                     if turma.lower() in f.name.lower()]
        
        if not csvs_turma:
            messagebox.showerror("❌ Sem CSVs da turma", 
                f"Nenhum CSV com '{turma}' em csv_brutos/!\n\n"
                f"📋 Exemplo necessário:\n"
                f"  {turma}_Logica.csv\n"
                f"  {turma}_Redes.csv\n"
                f"  {turma}_Processos.csv\n"
                f"  {turma}_Carreira.csv")
            self.reset_btn()
            return
        
        # LOG
        self.log_text.delete(1.0, 'end')
        self.log(f"🚀 Iniciando {turma} semana {semana}")
        self.log(f"📁 CSVs encontrados ({len(csvs_turma)}): {[f.name for f in csvs_turma]}")
        
        # Executa steps (modo importável)
        steps = [
            ("pipeline_processa_csvs", pipeline_main, []),
            ("gera_painel_turma", painel_main, []),
            ("lista_pendencias_detalhada", lista_pendencias_main, [turma, semana]),
            ("gera_aviso_alunos", gera_aviso_alunos_main, [turma, semana])
        ]

        for nome, fn, args in steps:
            self.log(f"🔄 {nome}...")

            try:
                fn(*args)
                self.log(f"✅ {nome} OK")
            except Exception as e:
                self.log(f"❌ {nome} FALHOU: {e}")
                self.reset_btn()
                return
        
        self.log("🎉 CONCLUÍDO!")
        self.log("📁 painel_turmas/ ← Excel")
        self.log("📱 avisos_alunos/ ← WhatsApp")
        self.log("💾 debug.log salvo")
        messagebox.showinfo("✅ PRONTO!", f"{turma} semana {semana} OK!")
        self.reset_btn()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = Automatizador()
    app.run()
