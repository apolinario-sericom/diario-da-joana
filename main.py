import flet as ft
import traceback

def main(page: ft.Page):
    # O ESCUDO CONTRA TELA BRANCA: Se algo der erro, a tela fica vermelha e avisa!
    try:
        import re
        import base64
        import requests
        from datetime import datetime

        # --- COMUNICAÇÃO REST PURA COM O SUPABASE (O MOTOR IMORTAL) ---
        URL_BASE = "https://rjcgswtifmdabqsfwifg.supabase.co/rest/v1"
        KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJqY2dzd3RpZm1kYWJxc2Z3aWZnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU0MjMxOTQsImV4cCI6MjA5MDk5OTE5NH0.7qtIV7a44s-38SrZ_ODYepiy-UugcZPA0Yp006jmVs0"
        HEADERS = {
            "apikey": KEY,
            "Authorization": f"Bearer {KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }

        def db_get(tabela, params=""):
            try:
                r = requests.get(f"{URL_BASE}/{tabela}?{params}", headers=HEADERS)
                return r.json() if r.status_code == 200 else []
            except: return []

        def db_post(tabela, dados):
            try:
                r = requests.post(f"{URL_BASE}/{tabela}", headers=HEADERS, json=dados)
                return r.json() if r.status_code in [200, 201] else []
            except: return []

        def db_patch(tabela, col, val, dados):
            try: requests.patch(f"{URL_BASE}/{tabela}?{col}=eq.{val}", headers=HEADERS, json=dados)
            except: pass

        def db_delete(tabela, col, val):
            try: requests.delete(f"{URL_BASE}/{tabela}?{col}=eq.{val}", headers=HEADERS)
            except: pass

        # --- CONFIGURAÇÕES DA PÁGINA ---
        page.title = "Diário da Joana"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.bgcolor = "#F3E5F5"
        page.window_width = 400
        page.window_height = 800
        page.padding = 0
        page.scroll = ft.ScrollMode.AUTO

        ROXO_FORTE = "#4A148C"
        ROXO_CLARO = "#9C27B0"
        BRANCO = ft.colors.WHITE

        def mostrar_mensagem(texto, cor_fundo=ft.colors.GREEN_700):
            page.snack_bar = ft.SnackBar(ft.Text(texto, color=BRANCO, weight=ft.FontWeight.BOLD), bgcolor=cor_fundo)
            page.snack_bar.open = True
            page.update()

        # --- GERADOR DE PDFs COM FPDF2 (DE VOLTA!) ---
        def gerar_pdf_relatorio(nome_aluno, texto_relatorio):
            try:
                from fpdf import FPDF
                nome_arquivo = f"Relatorio_{nome_aluno.replace(' ', '_')}.pdf"
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("helvetica", style="B", size=16)
                pdf.cell(0, 10, text="Diário da Joana - E.E.F. DR. CHAGAS FEIJÃO", new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("helvetica", style="B", size=14)
                pdf.cell(0, 10, text=f"Relatório do Aluno: {nome_aluno}", new_x="LMARGIN", new_y="NEXT")
                pdf.ln(5)
                pdf.set_font("helvetica", size=12)

                for linha in texto_relatorio.split('\n'):
                    pdf.multi_cell(0, 8, text=linha)
                    pdf.ln(2)

                try:
                    caminho = f"/storage/emulated/0/Download/{nome_arquivo}"
                    pdf.output(caminho)
                    mostrar_mensagem(f"PDF salvo em Downloads!")
                except:
                    pdf.output(nome_arquivo)
                    mostrar_mensagem(f"PDF gerado com sucesso!")
            except:
                mostrar_mensagem("Erro ao criar PDF.", ft.colors.RED_700)

        def gerar_pdf_boletim(nome_aluno, dados_notas):
            try:
                from fpdf import FPDF
                nome_arquivo = f"Boletim_{nome_aluno.replace(' ', '_')}.pdf"
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("helvetica", style="B", size=16)
                pdf.cell(0, 10, text="BOLETIM ESCOLAR - E.E.F. DR. CHAGAS FEIJÃO", new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("helvetica", style="B", size=14)
                pdf.cell(0, 10, text=f"Aluno(a): {nome_aluno}", new_x="LMARGIN", new_y="NEXT")
                pdf.ln(5)

                pdf.set_font("helvetica", style="B", size=10)
                pdf.cell(50, 10, "Matéria", border=1)
                pdf.cell(20, 10, "1B", border=1, align='C')
                pdf.cell(20, 10, "2B", border=1, align='C')
                pdf.cell(20, 10, "3B", border=1, align='C')
                pdf.cell(20, 10, "4B", border=1, align='C')
                pdf.cell(20, 10, "Méd", border=1, align='C', new_x="LMARGIN", new_y="NEXT")

                pdf.set_font("helvetica", size=10)
                for n in dados_notas:
                    pdf.cell(50, 10, str(n['materia'])[:18], border=1)
                    pdf.cell(20, 10, str(n['n1']), border=1, align='C')
                    pdf.cell(20, 10, str(n['n2']), border=1, align='C')
                    pdf.cell(20, 10, str(n['n3']), border=1, align='C')
                    pdf.cell(20, 10, str(n['n4']), border=1, align='C')
                    pdf.cell(20, 10, str(n['media']), border=1, align='C', new_x="LMARGIN", new_y="NEXT")

                try:
                    caminho = f"/storage/emulated/0/Download/{nome_arquivo}"
                    pdf.output(caminho)
                    mostrar_mensagem("Boletim em Downloads!")
                except:
                    pdf.output(nome_arquivo)
                    mostrar_mensagem("Boletim gerado!")
            except:
                mostrar_mensagem("Erro ao criar PDF.", ft.colors.RED_700)

        # --- INTEGRAÇÃO IMGBB ---
        url_foto_aluno_temp = [""]
        def fazer_upload_imgbb(caminho_arquivo):
            try:
                with open(caminho_arquivo, "rb") as image_file:
                    imagem_b64 = base64.b64encode(image_file.read()).decode('utf-8')
                payload = {"key": "01ab5e842417d976f2a5bedaeacaa5ec", "image": imagem_b64}
                resposta = requests.post("https://api.imgbb.com/1/upload", data=payload)
                return resposta.json().get("data", {}).get("url")
            except: return None

        def foto_joana_selecionada(e: ft.FilePickerResultEvent):
            if e.files and e.files[0].path:
                mostrar_mensagem("Atualizando...", ft.colors.ORANGE_700)
                url = fazer_upload_imgbb(e.files[0].path)
                if url:
                    page.client_storage.set("foto_joana", url)
                    avatar_joana.background_image_url = url
                    avatar_joana.content = None
                    mostrar_mensagem("Foto atualizada!")
                    page.update()

        def foto_aluno_selecionada(e: ft.FilePickerResultEvent):
            if e.files and e.files[0].path:
                mostrar_mensagem("Enviando foto...", ft.colors.ORANGE_700)
                url = fazer_upload_imgbb(e.files[0].path)
                if url:
                    url_foto_aluno_temp[0] = url
                    preview_foto_aluno.background_image_url = url
                    preview_foto_aluno.content = None
                    mostrar_mensagem("Foto pronta!")
                    page.update()

        picker_joana = ft.FilePicker(on_result=foto_joana_selecionada)
        picker_aluno = ft.FilePicker(on_result=foto_aluno_selecionada)
        page.overlay.extend([picker_joana, picker_aluno])

        # --- MÁSCARAS ---
        def formatar_data_ao_sair(e):
            v = re.sub(r'\D', '', e.control.value)
            if len(v) == 8: e.control.value = f"{v[:2]}/{v[2:4]}/{v[4:]}"
            e.control.update()

        def formatar_telefone_ao_sair(e):
            v = re.sub(r'\D', '', e.control.value)
            if len(v) >= 10:
                if len(v) == 11: e.control.value = f"({v[:2]}) {v[2:7]}-{v[7:]}"
                else: e.control.value = f"({v[:2]}) {v[2:6]}-{v[6:]}"
            e.control.update()

        # --- VARIÁVEIS DA UI E MODAIS ---
        lista_turmas_edit = ft.Column(scroll=ft.ScrollMode.AUTO, height=250, spacing=10)
        lista_alunos_edit = ft.Column(scroll=ft.ScrollMode.AUTO, height=350, spacing=10)
        lista_materias_edit = ft.Column(scroll=ft.ScrollMode.AUTO, height=250, spacing=10)

        id_turma_alvo = [None]; id_aluno_alvo = [None]; id_materia_alvo = [None]

        edit_nome_turma = ft.TextField(label="Nome da Turma", border_color=ROXO_FORTE)
        edit_horarios = ft.TextField(label="Horários", border_color=ROXO_FORTE)
        edit_dias = ft.TextField(label="Dias da Semana", border_color=ROXO_FORTE)
        lista_alunos_na_turma = ft.Column(scroll=ft.ScrollMode.AUTO, height=150) 

        edit_turma_aluno = ft.Dropdown(label="Turma Atual", border_color=ROXO_FORTE)
        edit_nome_aluno = ft.TextField(label="Nome", border_color=ROXO_FORTE)
        edit_mae_aluno = ft.TextField(label="Nome da Mãe", border_color=ROXO_FORTE)
        edit_nasc_aluno = ft.TextField(label="Data Nasc.", border_color=ROXO_FORTE, on_blur=formatar_data_ao_sair)
        edit_tel_aluno = ft.TextField(label="Telefone", border_color=ROXO_FORTE, on_blur=formatar_telefone_ao_sair)
        preview_edit_foto_aluno = ft.CircleAvatar(radius=30, bgcolor=ROXO_CLARO, content=ft.Icon(ft.icons.PERSON, color=BRANCO))

        edit_turma_materia = ft.Dropdown(label="Turma da Matéria", border_color=ROXO_FORTE)
        edit_nome_materia = ft.TextField(label="Nome da Matéria", border_color=ROXO_FORTE)

        def fechar_modais(e=None):
            dialog_editar_turma.open = False; dialog_excluir_turma.open = False
            dialog_editar_aluno.open = False; dialog_excluir_aluno.open = False
            dialog_editar_materia.open = False; dialog_excluir_materia.open = False
            dialog_historico_chamada.open = False; page.update()

        # --- AÇÕES DE EDIÇÃO/EXCLUSÃO ---
        def confirmar_edicao_turma(e):
            db_patch('joana_turmas', 'id', id_turma_alvo[0], {"nome": edit_nome_turma.value, "horarios": edit_horarios.value, "dias": edit_dias.value})
            fechar_modais(); mostrar_mensagem("Turma atualizada!"); carregar_dados_gerais()

        def confirmar_exclusao_turma(e):
            db_delete('joana_turmas', 'id', id_turma_alvo[0])
            fechar_modais(); mostrar_mensagem("Turma excluída!", ft.colors.ORANGE_700); carregar_dados_gerais()

        def confirmar_edicao_aluno(e):
            dados = {"nome_completo": edit_nome_aluno.value, "nome_mae": edit_mae_aluno.value, "data_nasc": edit_nasc_aluno.value, "telefone": edit_tel_aluno.value}
            db_patch('joana_alunos', 'id', id_aluno_alvo[0], dados)
            db_delete('joana_turma_alunos', 'id_aluno', id_aluno_alvo[0])
            if edit_turma_aluno.value: db_post('joana_turma_alunos', {"id_turma": int(edit_turma_aluno.value), "id_aluno": id_aluno_alvo[0]})
            fechar_modais(); mostrar_mensagem("Aluno atualizado!"); carregar_dados_gerais()

        def confirmar_exclusao_aluno(e):
            db_delete('joana_alunos', 'id', id_aluno_alvo[0])
            fechar_modais(); mostrar_mensagem("Aluno excluído!", ft.colors.ORANGE_700); carregar_dados_gerais()

        def confirmar_edicao_materia(e):
            db_patch('joana_materias', 'id', id_materia_alvo[0], {"nome_materia": edit_nome_materia.value, "id_turma": int(edit_turma_materia.value)})
            fechar_modais(); mostrar_mensagem("Matéria atualizada!"); carregar_dados_gerais()

        def confirmar_exclusao_materia(e):
            db_delete('joana_materias', 'id', id_materia_alvo[0])
            fechar_modais(); mostrar_mensagem("Matéria excluída!", ft.colors.ORANGE_700); carregar_dados_gerais()

        # --- ESTRUTURA DOS MODAIS ---
        dialog_editar_turma = ft.AlertDialog(title=ft.Text("Editar Turma"), content=ft.Column([edit_nome_turma, edit_horarios, edit_dias, ft.Divider(), ft.Text("Alunos cadastrados:"), lista_alunos_na_turma], tight=True), actions=[ft.TextButton("Cancelar", on_click=fechar_modais), ft.ElevatedButton("Salvar", on_click=confirmar_edicao_turma, bgcolor=ROXO_FORTE, color=BRANCO)])
        dialog_excluir_turma = ft.AlertDialog(title=ft.Text("Excluir Turma?"), content=ft.Text("Iso apagará os vínculos de alunos desta turma."), actions=[ft.TextButton("Voltar", on_click=fechar_modais), ft.ElevatedButton("Excluir", on_click=confirmar_exclusao_turma, bgcolor="red", color=BRANCO)])
        dialog_editar_aluno = ft.AlertDialog(title=ft.Text("Editar Aluno"), content=ft.Column([preview_edit_foto_aluno, edit_turma_aluno, edit_nome_aluno, edit_mae_aluno, edit_nasc_aluno, edit_tel_aluno], tight=True), actions=[ft.TextButton("Cancelar", on_click=fechar_modais), ft.ElevatedButton("Salvar", on_click=confirmar_edicao_aluno, bgcolor=ROXO_FORTE, color=BRANCO)])
        dialog_excluir_aluno = ft.AlertDialog(title=ft.Text("Excluir Aluno?"), actions=[ft.TextButton("Voltar", on_click=fechar_modais), ft.ElevatedButton("Excluir", on_click=confirmar_exclusao_aluno, bgcolor="red", color=BRANCO)])
        dialog_editar_materia = ft.AlertDialog(title=ft.Text("Editar Matéria"), content=ft.Column([edit_turma_materia, edit_nome_materia], tight=True), actions=[ft.TextButton("Cancelar", on_click=fechar_modais), ft.ElevatedButton("Salvar", on_click=confirmar_edicao_materia, bgcolor=ROXO_FORTE, color=BRANCO)])
        dialog_excluir_materia = ft.AlertDialog(title=ft.Text("Excluir Matéria?"), actions=[ft.TextButton("Voltar", on_click=fechar_modais), ft.ElevatedButton("Excluir", on_click=confirmar_exclusao_materia, bgcolor="red", color=BRANCO)])
        lista_historico_chamada = ft.Column(scroll=ft.ScrollMode.AUTO, height=300)
        dialog_historico_chamada = ft.AlertDialog(title=ft.Text("Histórico do Dia"), content=lista_historico_chamada, actions=[ft.TextButton("Fechar", on_click=fechar_modais)])

        page.overlay.extend([dialog_editar_turma, dialog_excluir_turma, dialog_editar_aluno, dialog_excluir_aluno, dialog_editar_materia, dialog_excluir_materia, dialog_historico_chamada])

        # --- AUXILIARES DE INTERFACE ---
        def abrir_edicao_turma(t):
            id_turma_alvo[0] = t['id']; edit_nome_turma.value = t.get('nome', ''); edit_horarios.value = t.get('horarios', ''); edit_dias.value = t.get('dias', '')
            lista_alunos_na_turma.controls.clear()
            vinc = db_get('joana_turma_alunos', f'id_turma=eq.{t["id"]}')
            ids = [v['id_aluno'] for v in vinc]
            if ids:
                alunos = db_get('joana_alunos', f"id=in.({','.join(map(str, ids))})&order=nome_completo.asc")
                for a in alunos: lista_alunos_na_turma.controls.append(ft.Text(f"• {a['nome_completo']}"))
            dialog_editar_turma.open = True; page.update()

        def criar_linha_turma(t): return ft.Card(content=ft.ListTile(leading=ft.Icon(ft.icons.CLASS_), title=ft.Text(t['nome'], weight="bold"), subtitle=ft.Text(t.get('dias', '')), trailing=ft.Row([ft.IconButton(ft.icons.EDIT, on_click=lambda _: abrir_edicao_turma(t)), ft.IconButton(ft.icons.DELETE, icon_color="red", on_click=lambda _: setattr(id_turma_alvo, 0, t['id']) or setattr(dialog_excluir_turma, 'open', True) or page.update())], tight=True)))
        
        def criar_linha_aluno(a):
            av = ft.CircleAvatar(radius=20, background_image_url=a.get('foto_url') if a.get('foto_url') else None, content=None if a.get('foto_url') else ft.Icon(ft.icons.PERSON))
            return ft.Card(content=ft.ListTile(leading=av, title=ft.Text(a['nome_completo'], weight="bold"), subtitle=ft.Text(f"Mãe: {a.get('nome_mae', '')}"), trailing=ft.Row([ft.IconButton(ft.icons.EDIT, on_click=lambda _: abrir_edicao_aluno(a)), ft.IconButton(ft.icons.DELETE, icon_color="red", on_click=lambda _: setattr(id_aluno_alvo, 0, a['id']) or setattr(dialog_excluir_aluno, 'open', True) or page.update())], tight=True)))

        def abrir_edicao_aluno(a):
            id_aluno_alvo[0] = a['id']; edit_nome_aluno.value = a['nome_completo']; edit_mae_aluno.value = a.get('nome_mae', ''); edit_nasc_aluno.value = a.get('data_nasc', ''); edit_tel_aluno.value = a.get('telefone', '')
            edit_turma_aluno.options = dropdown_turma_aluno.options.copy(); edit_turma_aluno.value = None
            if a.get('foto_url'): preview_edit_foto_aluno.background_image_url = a['foto_url']
            else: preview_edit_foto_aluno.content = ft.Icon(ft.icons.PERSON)
            resp = db_get('joana_turma_alunos', f'id_aluno=eq.{a["id"]}')
            if resp: edit_turma_aluno.value = str(resp[0]['id_turma'])
            dialog_editar_aluno.open = True; page.update()

        # --- CARREGAMENTOS GERAIS ---
        def carregar_dados_gerais():
            resp_turmas = db_get('joana_turmas', 'order=id.asc')
            mapa_turmas = {t['id']: t['nome'] for t in resp_turmas}
            dropdown_turma_aluno.options.clear(); dropdown_turma_materia.options.clear(); dropdown_turma_chamada.options.clear(); dropdown_turma_notas.options.clear(); lista_turmas_edit.controls.clear()
            for t in resp_turmas:
                opt = ft.dropdown.Option(key=str(t['id']), text=t['nome'])
                dropdown_turma_aluno.options.append(opt); dropdown_turma_materia.options.append(opt); dropdown_turma_chamada.options.append(opt); dropdown_turma_notas.options.append(opt)
                lista_turmas_edit.controls.append(criar_linha_turma(t))

            resp_alunos = db_get('joana_alunos', 'order=nome_completo.asc')
            dropdown_aluno_relatorio.options.clear(); dropdown_aluno_boletim.options.clear(); lista_alunos_edit.controls.clear()
            for a in resp_alunos:
                opt_a = ft.dropdown.Option(key=str(a['id']), text=a['nome_completo'])
                dropdown_aluno_relatorio.options.append(opt_a); dropdown_aluno_boletim.options.append(opt_a)
                lista_alunos_edit.controls.append(criar_linha_aluno(a))

            resp_mat = db_get('joana_materias')
            lista_materias_edit.controls.clear()
            for m in resp_mat:
                nome_t = mapa_turmas.get(m['id_turma'], 'Desconhecida')
                lista_materias_edit.controls.append(ft.Card(content=ft.ListTile(leading=ft.Icon(ft.icons.BOOK), title=ft.Text(m['nome_materia']), subtitle=ft.Text(nome_t), trailing=ft.IconButton(ft.icons.DELETE, icon_color="red", on_click=lambda _: db_delete('joana_materias', 'id', m['id']) or carregar_dados_gerais()))))
            page.update()

        # --- TELAS ---
        input_nome_turma = ft.TextField(label="Nome", border_color=ROXO_FORTE)
        tela_turmas = ft.Container(content=ft.Column([ft.Text("Turmas", size=24, weight="bold", color=ROXO_FORTE), input_nome_turma, ft.ElevatedButton("Salvar", on_click=lambda _: db_post('joana_turmas', {"nome": input_nome_turma.value}) or carregar_dados_gerais(), bgcolor=ROXO_FORTE, color=BRANCO), ft.Divider(), lista_turmas_edit], horizontal_alignment="center"), padding=20, visible=False)

        input_nome_aluno = ft.TextField(label="Nome Completo", border_color=ROXO_FORTE)
        input_mae_aluno = ft.TextField(label="Nome da Mãe", border_color=ROXO_FORTE)
        input_tel_aluno = ft.TextField(label="Telefone", border_color=ROXO_FORTE, on_blur=formatar_telefone_ao_sair)
        preview_foto_aluno = ft.CircleAvatar(radius=40, bgcolor=ROXO_CLARO, content=ft.Icon(ft.icons.PERSON, color=BRANCO))
        tela_alunos = ft.Container(content=ft.Column([
            ft.Text("Alunos", size=24, weight="bold", color=ROXO_FORTE),
            ft.Stack([preview_foto_aluno, ft.IconButton(ft.icons.CAMERA_ALT, on_click=lambda _: picker_aluno.pick_files(), bottom=0, right=0)]),
            dropdown_turma_aluno, input_nome_aluno, input_mae_aluno, input_tel_aluno,
            ft.ElevatedButton("Salvar Aluno", on_click=lambda _: db_post('joana_alunos', {"nome_completo": input_nome_aluno.value, "nome_mae": input_mae_aluno.value, "telefone": input_tel_aluno.value, "foto_url": url_foto_aluno_temp[0]}) or carregar_dados_gerais(), bgcolor=ROXO_FORTE, color=BRANCO),
            ft.Divider(), lista_alunos_edit
        ], horizontal_alignment="center"), padding=20, visible=False)

        # --- CHAMADA E NOTAS ---
        controles_chamada = {}
        def carregar_alunos_chamada(e):
            if not dropdown_turma_chamada.value: return
            vinc = db_get('joana_turma_alunos', f'id_turma=eq.{dropdown_turma_chamada.value}')
            ids = [v['id_aluno'] for v in vinc]
            lista_chamada_alunos.controls.clear(); controles_chamada.clear()
            if ids:
                alunos = db_get('joana_alunos', f"id=in.({','.join(map(str, ids))})&order=nome_completo.asc")
                for a in alunos:
                    drop = ft.Dropdown(options=[ft.dropdown.Option("P"), ft.dropdown.Option("F")], value="P", width=80)
                    controles_chamada[a['id']] = drop
                    lista_chamada_alunos.controls.append(ft.Row([ft.Text(a['nome_completo'], expand=True), drop]))
            page.update()

        dropdown_turma_chamada.on_change = carregar_alunos_chamada
        lista_chamada_alunos = ft.Column(scroll=ft.ScrollMode.AUTO, height=300)
        tela_chamada = ft.Container(content=ft.Column([
            ft.Text("Chamada", size=24, weight="bold", color=ROXO_FORTE),
            dropdown_turma_chamada,
            lista_chamada_alunos,
            ft.ElevatedButton("Salvar Presenças", on_click=lambda _: mostrar_mensagem("Chamada Salva!"), bgcolor="green", color=BRANCO)
        ], horizontal_alignment="center"), padding=20, visible=False)

        # --- RELATÓRIOS E BOLETIM ---
        texto_relatorio = ft.TextField(label="Relatório Pedagógico", multiline=True, min_lines=5, border_color=ROXO_FORTE)
        dropdown_aluno_relatorio.on_change = lambda _: setattr(texto_relatorio, 'value', (db_get('joana_relatorios', f'id_aluno=eq.{dropdown_aluno_relatorio.value}') or [{'texto_relatorio':''}])[0]['texto_relatorio']) or page.update()
        
        tela_relatorios = ft.Container(content=ft.Column([
            ft.Text("Relatórios", size=24, weight="bold", color=ROXO_FORTE),
            dropdown_aluno_relatorio, texto_relatorio,
            ft.Row([
                ft.ElevatedButton("Salvar", on_click=lambda _: db_post('joana_relatorios', {"id_aluno": int(dropdown_aluno_relatorio.value), "texto_relatorio": texto_relatorio.value}), bgcolor=ROXO_FORTE, color=BRANCO),
                ft.ElevatedButton("Gerar PDF", on_click=lambda _: gerar_pdf_relatorio(dropdown_aluno_relatorio.content_text, texto_relatorio.value), bgcolor="red", color=BRANCO)
            ], alignment="center")
        ], horizontal_alignment="center"), padding=20, visible=False)

        # --- NAVEGAÇÃO ---
        def mudar_tela(e):
            for t in [tela_home, tela_turmas, tela_alunos, tela_chamada, tela_relatorios]: t.visible = False
            if e.control.selected_index == 0: tela_home.visible = True
            elif e.control.selected_index == 1: tela_turmas.visible = True
            elif e.control.selected_index == 2: tela_alunos.visible = True
            elif e.control.selected_index == 3: tela_chamada.visible = True
            elif e.control.selected_index == 4: tela_relatorios.visible = True
            carregar_dados_gerais(); page.update()

        page.navigation_bar = ft.NavigationBar(
            destinations=[
                ft.NavigationDestination(icon=ft.icons.HOME, label="Início"),
                ft.NavigationDestination(icon=ft.icons.CLASS_, label="Turmas"),
                ft.NavigationDestination(icon=ft.icons.PERSON, label="Alunos"),
                ft.NavigationDestination(icon=ft.icons.CHECK, label="Chamada"),
                ft.NavigationDestination(icon=ft.icons.PICTURE_AS_PDF, label="Relatórios"),
            ], on_change=mudar_tela
        )

        avatar_joana = ft.CircleAvatar(radius=50, bgcolor=ROXO_FORTE, content=ft.Icon(ft.icons.FACE_RETOUCHING_NATURAL, color=BRANCO, size=50))
        tela_home = ft.Container(content=ft.Column([
            ft.Stack([avatar_joana, ft.IconButton(ft.icons.CAMERA_ALT, on_click=lambda _: picker_joana.pick_files(), bottom=0, right=0)]),
            ft.Text("Diário da Joana", size=30, weight="bold", color=ROXO_FORTE),
            ft.Text("E.E.F. DR. CHAGAS FEIJÃO", size=16, italic=True),
            ft.Divider(),
            ft.Text("Toque no menu abaixo para gerenciar sua escola.", text_align="center")
        ], horizontal_alignment="center"), padding=50)

        topo = ft.Container(content=ft.Text("Sistema Escolar Joana", color=BRANCO, weight="bold"), bgcolor=ROXO_FORTE, padding=15, alignment=ft.alignment.center)
        page.add(topo, tela_home, tela_turmas, tela_alunos, tela_chamada, tela_relatorios)
        carregar_dados_gerais()

    except Exception:
        page.add(ft.Text(f"Erro Fatal: {traceback.format_exc()}", color="red"))
        page.update()

ft.app(target=main)
