import flet as ft
import traceback

def main(page: ft.Page):
    # A MÁGICA TÁ AQUI: Só carregamos as coisas DEPOIS que a tela do celular já tá viva!
    try:
        import re
        import base64
        import requests
        from datetime import datetime
        import textwrap
        from supabase import create_client, Client
        from fpdf import FPDF

        # --- CONEXÃO SUPABASE ---
        URL = "https://rjcgswtifmdabqsfwifg.supabase.co"
        KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJqY2dzd3RpZm1kYWJxc2Z3aWZnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU0MjMxOTQsImV4cCI6MjA5MDk5OTE5NH0.7qtIV7a44s-38SrZ_ODYepiy-UugcZPA0Yp006jmVs0"
        supabase: Client = create_client(URL, KEY)

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

        # --- GERADORES DE PDF ---
        def gerar_pdf_relatorio(nome_aluno, texto_relatorio):
            try:
                nome_arquivo = f"Relatorio_{nome_aluno.replace(' ', '_')}.pdf"
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("helvetica", style="B", size=16)
                pdf.cell(0, 10, text="Diário da Joana - E.E.F. DR. CHAGAS FEIJÃO", new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("helvetica", style="B", size=14)
                pdf.cell(0, 10, text=f"Relatório do Aluno: {nome_aluno}", new_x="LMARGIN", new_y="NEXT")
                pdf.ln(5)
                pdf.set_font("helvetica", size=12)

                for linha_orig in texto_relatorio.split('\n'):
                    pdf.multi_cell(0, 8, text=linha_orig)
                    pdf.ln(2)

                try:
                    caminho = f"/storage/emulated/0/Download/{nome_arquivo}"
                    pdf.output(caminho)
                except:
                    pdf.output(nome_arquivo)
                
                mostrar_mensagem(f"PDF salvo: {nome_arquivo}")
            except Exception as e:
                mostrar_mensagem(f"Erro PDF", ft.colors.RED_700)

        def gerar_pdf_boletim(nome_aluno, dados_notas):
            try:
                nome_arquivo = f"Boletim_{nome_aluno.replace(' ', '_')}.pdf"
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("helvetica", style="B", size=16)
                pdf.cell(0, 10, text="BOLETIM ESCOLAR - E.E.F. DR. CHAGAS FEIJÃO", new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("helvetica", style="B", size=14)
                pdf.cell(0, 10, text=f"Aluno(a): {nome_aluno}", new_x="LMARGIN", new_y="NEXT")
                pdf.ln(5)

                pdf.set_font("helvetica", style="B", size=12)
                pdf.cell(60, 10, "Matéria", border=1)
                pdf.cell(25, 10, "1 Bim", border=1, align='C')
                pdf.cell(25, 10, "2 Bim", border=1, align='C')
                pdf.cell(25, 10, "3 Bim", border=1, align='C')
                pdf.cell(25, 10, "4 Bim", border=1, align='C')
                pdf.cell(30, 10, "Média", border=1, align='C', new_x="LMARGIN", new_y="NEXT")

                pdf.set_font("helvetica", size=12)
                for nota in dados_notas:
                    pdf.cell(60, 10, str(nota['materia'])[:20], border=1)
                    pdf.cell(25, 10, str(nota['n1']), border=1, align='C')
                    pdf.cell(25, 10, str(nota['n2']), border=1, align='C')
                    pdf.cell(25, 10, str(nota['n3']), border=1, align='C')
                    pdf.cell(25, 10, str(nota['n4']), border=1, align='C')
                    pdf.cell(30, 10, str(nota['media']), border=1, align='C', new_x="LMARGIN", new_y="NEXT")

                try:
                    caminho = f"/storage/emulated/0/Download/{nome_arquivo}"
                    pdf.output(caminho)
                except:
                    pdf.output(nome_arquivo)
                    
                mostrar_mensagem(f"Boletim salvo: {nome_arquivo}")
            except Exception as e:
                mostrar_mensagem(f"Erro PDF", ft.colors.RED_700)

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
                else: mostrar_mensagem("Erro foto.", ft.colors.RED_700)

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
                else: mostrar_mensagem("Erro foto.", ft.colors.RED_700)

        picker_joana = ft.FilePicker(on_result=foto_joana_selecionada)
        picker_aluno = ft.FilePicker(on_result=foto_aluno_selecionada)
        page.overlay.extend([picker_joana, picker_aluno])

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

        lista_turmas_edit = ft.Column(scroll=ft.ScrollMode.AUTO, height=250, spacing=10)
        lista_alunos_edit = ft.Column(scroll=ft.ScrollMode.AUTO, height=350, spacing=10)
        lista_materias_edit = ft.Column(scroll=ft.ScrollMode.AUTO, height=250, spacing=10)

        id_turma_alvo = [None]
        id_aluno_alvo = [None]
        id_materia_alvo = [None]

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
            dialog_editar_turma.open = False
            dialog_excluir_turma.open = False
            dialog_editar_aluno.open = False
            dialog_excluir_aluno.open = False
            dialog_editar_materia.open = False
            dialog_excluir_materia.open = False
            dialog_historico_chamada.open = False
            page.update()

        def confirmar_edicao_turma(e):
            try:
                supabase.table('joana_turmas').update({"nome": edit_nome_turma.value, "horarios": edit_horarios.value, "dias": edit_dias.value}).eq('id', id_turma_alvo[0]).execute()
                fechar_modais()
                mostrar_mensagem("Turma atualizada!")
                carregar_dados_gerais()
            except: mostrar_mensagem("Erro ao atualizar.", ft.colors.RED_700)

        def confirmar_exclusao_turma(e):
            try:
                supabase.table('joana_turmas').delete().eq('id', id_turma_alvo[0]).execute()
                fechar_modais()
                mostrar_mensagem("Turma excluída!", ft.colors.ORANGE_700)
                carregar_dados_gerais()
            except: 
                fechar_modais()
                mostrar_mensagem("Remova alunos/matérias primeiro.", ft.colors.RED_700)

        def confirmar_edicao_aluno(e):
            try:
                dados = {"nome_completo": edit_nome_aluno.value, "nome_mae": edit_mae_aluno.value, "data_nasc": edit_nasc_aluno.value, "telefone": edit_tel_aluno.value}
                supabase.table('joana_alunos').update(dados).eq('id', id_aluno_alvo[0]).execute()
                supabase.table('joana_turma_alunos').delete().eq('id_aluno', id_aluno_alvo[0]).execute()
                if edit_turma_aluno.value: 
                    supabase.table('joana_turma_alunos').insert({"id_turma": int(edit_turma_aluno.value), "id_aluno": id_aluno_alvo[0]}).execute()
                fechar_modais()
                mostrar_mensagem("Aluno atualizado!")
                carregar_dados_gerais()
            except: 
                fechar_modais()
                mostrar_mensagem("Erro atualizar.", ft.colors.RED_700)

        def confirmar_exclusao_aluno(e):
            try:
                supabase.table('joana_alunos').delete().eq('id', id_aluno_alvo[0]).execute()
                fechar_modais()
                mostrar_mensagem("Aluno excluído!", ft.colors.ORANGE_700)
                carregar_dados_gerais()
            except: 
                fechar_modais()
                mostrar_mensagem("Erro excluir.", ft.colors.RED_700)

        def confirmar_edicao_materia(e):
            try:
                supabase.table('joana_materias').update({"nome_materia": edit_nome_materia.value, "id_turma": int(edit_turma_materia.value)}).eq('id', id_materia_alvo[0]).execute()
                fechar_modais()
                mostrar_mensagem("Matéria atualizada!")
                carregar_dados_gerais()
            except: mostrar_mensagem("Erro.", ft.colors.RED_700)

        def confirmar_exclusao_materia(e):
            try:
                supabase.table('joana_materias').delete().eq('id', id_materia_alvo[0]).execute()
                fechar_modais()
                mostrar_mensagem("Matéria excluída!", ft.colors.ORANGE_700)
                carregar_dados_gerais()
            except: mostrar_mensagem("Erro.", ft.colors.RED_700)

        dialog_editar_turma = ft.AlertDialog(title=ft.Text("Editar Turma", color=ROXO_FORTE), content=ft.Column([edit_nome_turma, edit_horarios, edit_dias, ft.Divider(), ft.Text("Alunos:"), lista_alunos_na_turma], tight=True), actions=[ft.TextButton("Cancelar", on_click=fechar_modais), ft.ElevatedButton("Salvar", bgcolor=ROXO_FORTE, color=BRANCO, on_click=confirmar_edicao_turma)])
        dialog_excluir_turma = ft.AlertDialog(title=ft.Text("Excluir?", color="red"), content=ft.Text("Sem volta!"), actions=[ft.TextButton("Cancelar", on_click=fechar_modais), ft.ElevatedButton("Excluir", bgcolor="red", color=BRANCO, on_click=confirmar_exclusao_turma)])
        dialog_editar_aluno = ft.AlertDialog(title=ft.Text("Editar Aluno", color=ROXO_FORTE), content=ft.Column([preview_edit_foto_aluno, edit_turma_aluno, edit_nome_aluno, edit_mae_aluno, edit_nasc_aluno, edit_tel_aluno], tight=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER), actions=[ft.TextButton("Cancelar", on_click=fechar_modais), ft.ElevatedButton("Salvar", bgcolor=ROXO_FORTE, color=BRANCO, on_click=confirmar_edicao_aluno)])
        dialog_excluir_aluno = ft.AlertDialog(title=ft.Text("Excluir?", color="red"), content=ft.Text("Apagar do sistema?"), actions=[ft.TextButton("Cancelar", on_click=fechar_modais), ft.ElevatedButton("Excluir", bgcolor="red", color=BRANCO, on_click=confirmar_exclusao_aluno)])
        dialog_editar_materia = ft.AlertDialog(title=ft.Text("Editar Matéria", color=ROXO_FORTE), content=ft.Column([edit_turma_materia, edit_nome_materia], tight=True), actions=[ft.TextButton("Cancelar", on_click=fechar_modais), ft.ElevatedButton("Salvar", bgcolor=ROXO_FORTE, color=BRANCO, on_click=confirmar_edicao_materia)])
        dialog_excluir_materia = ft.AlertDialog(title=ft.Text("Excluir?", color="red"), content=ft.Text("Apagar?"), actions=[ft.TextButton("Cancelar", on_click=fechar_modais), ft.ElevatedButton("Excluir", bgcolor="red", color=BRANCO, on_click=confirmar_exclusao_materia)])
        lista_historico_chamada = ft.Column(scroll=ft.ScrollMode.AUTO, height=300)
        dialog_historico_chamada = ft.AlertDialog(title=ft.Text("Histórico", color=ROXO_FORTE), content=lista_historico_chamada, actions=[ft.TextButton("Fechar", on_click=fechar_modais)])

        page.overlay.extend([dialog_editar_turma, dialog_excluir_turma, dialog_editar_aluno, dialog_excluir_aluno, dialog_editar_materia, dialog_excluir_materia, dialog_historico_chamada])

        def abrir_edicao_turma(t):
            id_turma_alvo[0] = t['id']; edit_nome_turma.value = t.get('nome', ''); edit_horarios.value = t.get('horarios', ''); edit_dias.value = t.get('dias', '')
            lista_alunos_na_turma.controls.clear()
            try:
                ids = [i['id_aluno'] for i in supabase.table('joana_turma_alunos').select('id_aluno').eq('id_turma', t['id']).execute().data]
                if ids:
                    for a in supabase.table('joana_alunos').select('nome_completo').in_('id', ids).order('nome_completo').execute().data:
                        lista_alunos_na_turma.controls.append(ft.Text(f"• {a['nome_completo']}"))
            except: pass
            dialog_editar_turma.open = True; page.update()

        def abrir_exclusao_turma(id_t): id_turma_alvo[0] = id_t; dialog_excluir_turma.open = True; page.update()

        def abrir_edicao_aluno(a):
            id_aluno_alvo[0] = a['id']; edit_nome_aluno.value = a.get('nome_completo', ''); edit_mae_aluno.value = a.get('nome_mae', ''); edit_nasc_aluno.value = a.get('data_nasc', ''); edit_tel_aluno.value = a.get('telefone', '')
            edit_turma_aluno.options = dropdown_turma_aluno.options.copy(); edit_turma_aluno.value = None
            if a.get('foto_url'): 
                preview_edit_foto_aluno.background_image_url = a['foto_url']
                preview_edit_foto_aluno.content = None
            else:
                preview_edit_foto_aluno.background_image_url = None
                preview_edit_foto_aluno.content = ft.Icon(ft.icons.PERSON, color=BRANCO)
            try:
                resp = supabase.table('joana_turma_alunos').select('id_turma').eq('id_aluno', a['id']).execute()
                if resp.data: edit_turma_aluno.value = str(resp.data[0]['id_turma'])
            except: pass
            dialog_editar_aluno.open = True; page.update()

        def abrir_exclusao_aluno(id_a): id_aluno_alvo[0] = id_a; dialog_excluir_aluno.open = True; page.update()

        def abrir_edicao_materia(m):
            id_materia_alvo[0] = m['id']; edit_nome_materia.value = m['nome_materia']
            edit_turma_materia.options = dropdown_turma_materia.options.copy(); edit_turma_materia.value = str(m['id_turma'])
            dialog_editar_materia.open = True; page.update()

        def abrir_exclusao_materia(id_m): id_materia_alvo[0] = id_m; dialog_excluir_materia.open = True; page.update()

        def criar_linha_turma(t): return ft.Card(content=ft.ListTile(leading=ft.Icon(ft.icons.CLASS_, color=ROXO_CLARO), title=ft.Text(t['nome'], weight=ft.FontWeight.BOLD), subtitle=ft.Text(f"{t.get('dias', '')}"), trailing=ft.Row([ft.IconButton(ft.icons.EDIT, icon_color=ROXO_FORTE, on_click=lambda e: abrir_edicao_turma(t)), ft.IconButton(ft.icons.DELETE, icon_color="red", on_click=lambda e: abrir_exclusao_turma(t['id']))], tight=True)))
        def criar_linha_aluno(a):
            avatar = ft.CircleAvatar(radius=20, background_image_url=a.get('foto_url') if a.get('foto_url') else None, content=None if a.get('foto_url') else ft.Icon(ft.icons.PERSON), bgcolor=ROXO_CLARO)
            return ft.Card(content=ft.ListTile(leading=avatar, title=ft.Text(a['nome_completo'], weight=ft.FontWeight.BOLD), subtitle=ft.Text(f"Mãe: {a.get('nome_mae', '')}"), trailing=ft.Row([ft.IconButton(ft.icons.EDIT, icon_color=ROXO_FORTE, on_click=lambda e: abrir_edicao_aluno(a)), ft.IconButton(ft.icons.DELETE, icon_color="red", on_click=lambda e: abrir_exclusao_aluno(a['id']))], tight=True)))
        def criar_linha_materia(m, nome_turma): return ft.Card(content=ft.ListTile(leading=ft.Icon(ft.icons.MENU_BOOK, color=ROXO_CLARO), title=ft.Text(m['nome_materia'], weight=ft.FontWeight.BOLD), subtitle=ft.Text(nome_turma), trailing=ft.Row([ft.IconButton(ft.icons.EDIT, icon_color=ROXO_FORTE, on_click=lambda e: abrir_edicao_materia(m)), ft.IconButton(ft.icons.DELETE, icon_color="red", on_click=lambda e: abrir_exclusao_materia(m['id']))], tight=True)))

        def carregar_dados_gerais():
            try:
                resp_turmas = supabase.table('joana_turmas').select('*').order('id', desc=False).execute()
                mapa_turmas = {t['id']: t['nome'] for t in resp_turmas.data}
                dropdown_turma_aluno.options.clear(); dropdown_turma_materia.options.clear(); dropdown_turma_chamada.options.clear(); dropdown_turma_notas.options.clear(); lista_turmas_edit.controls.clear()
                for t in resp_turmas.data:
                    opcao = ft.dropdown.Option(key=str(t['id']), text=t['nome'])
                    dropdown_turma_aluno.options.append(opcao); dropdown_turma_materia.options.append(opcao); dropdown_turma_chamada.options.append(opcao); dropdown_turma_notas.options.append(opcao)
                    lista_turmas_edit.controls.append(criar_linha_turma(t))

                resp_alunos = supabase.table('joana_alunos').select('*').order('nome_completo').execute()
                dropdown_aluno_relatorio.options.clear(); dropdown_aluno_boletim.options.clear(); lista_alunos_edit.controls.clear()
                for a in resp_alunos.data:
                    opcao_aluno = ft.dropdown.Option(key=str(a['id']), text=a['nome_completo'])
                    dropdown_aluno_relatorio.options.append(opcao_aluno); dropdown_aluno_boletim.options.append(opcao_aluno)
                    lista_alunos_edit.controls.append(criar_linha_aluno(a))

                resp_mat = supabase.table('joana_materias').select('*').execute()
                lista_materias_edit.controls.clear()
                for m in resp_mat.data:
                    nome_t = mapa_turmas.get(m['id_turma'], 'Desconhecida')
                    lista_materias_edit.controls.append(criar_linha_materia(m, nome_t))

                lista_turmas_edit.update(); lista_alunos_edit.update(); lista_materias_edit.update(); page.update()
            except: pass

        def acao_salvar_turma(e):
            if not input_nome_turma.value: return
            try:
                supabase.table('joana_turmas').insert({"nome": input_nome_turma.value, "horarios": input_horario_turma.value, "dias": input_dias_turma.value}).execute()
                mostrar_mensagem("Turma cadastrada!")
                input_nome_turma.value = input_horario_turma.value = input_dias_turma.value = ""; carregar_dados_gerais() 
            except: mostrar_mensagem("Erro.", ft.colors.RED_700)

        def acao_salvar_aluno(e):
            if not input_nome_aluno.value: return
            try:
                dados = {"nome_completo": input_nome_aluno.value, "nome_mae": input_mae_aluno.value, "data_nasc": input_nasc_aluno.value, "endereco": input_end_aluno.value, "telefone": input_tel_aluno.value, "foto_url": url_foto_aluno_temp[0]}
                resp = supabase.table('joana_alunos').insert(dados).execute()
                if dropdown_turma_aluno.value: supabase.table('joana_turma_alunos').insert({"id_turma": int(dropdown_turma_aluno.value), "id_aluno": resp.data[0]['id']}).execute()
                mostrar_mensagem("Aluno salvo!")
                input_nome_aluno.value = input_mae_aluno.value = input_nasc_aluno.value = input_end_aluno.value = input_tel_aluno.value = ""
                url_foto_aluno_temp[0] = ""
                preview_foto_aluno.background_image_url = None; preview_foto_aluno.content = ft.Icon(ft.icons.PERSON, color=BRANCO)
                carregar_dados_gerais()
            except Exception as e: print(e); mostrar_mensagem("Erro.", ft.colors.RED_700)

        def acao_salvar_materia(e):
            if not input_nome_materia.value or not dropdown_turma_materia.value: return
            try:
                supabase.table('joana_materias').insert({"nome_materia": input_nome_materia.value, "id_turma": int(dropdown_turma_materia.value)}).execute()
                mostrar_mensagem("Matéria cadastrada!")
                input_nome_materia.value = ""; carregar_dados_gerais()
            except: pass

        controles_chamada_alunos = {}
        def ao_mudar_turma_chamada(e):
            if not dropdown_turma_chamada.value: return
            try:
                ids = [i['id_aluno'] for i in supabase.table('joana_turma_alunos').select('id_aluno').eq('id_turma', int(dropdown_turma_chamada.value)).execute().data]
                lista_chamada_alunos.controls.clear(); controles_chamada_alunos.clear()
                if not ids: return page.update()
                for aluno in supabase.table('joana_alunos').select('id, nome_completo, foto_url').in_('id', ids).order('nome_completo').execute().data:
                    drop_status = ft.Dropdown(options=[ft.dropdown.Option("P", "P"), ft.dropdown.Option("F", "F"), ft.dropdown.Option("J", "J")], value="P", width=80, dense=True)
                    controles_chamada_alunos[aluno['id']] = drop_status
                    avatar = ft.CircleAvatar(radius=15, background_image_url=aluno.get('foto_url') if aluno.get('foto_url') else None, content=None if aluno.get('foto_url') else ft.Icon(ft.icons.PERSON, size=15))
                    lista_chamada_alunos.controls.append(ft.Row([avatar, ft.Text(aluno['nome_completo'], expand=True, weight=ft.FontWeight.BOLD), drop_status]))
                page.update()
            except: pass

        def acao_salvar_frequencia(e):
            if not dropdown_turma_chamada.value or not input_data_chamada.value: return
            try:
                d_br = input_data_chamada.value
                data_sql = f"{d_br[6:10]}-{d_br[3:5]}-{d_br[0:2]}"
                for id_aluno, drop_status in controles_chamada_alunos.items():
                    resp = supabase.table('joana_frequencia').select('id').eq('id_aluno', id_aluno).eq('data', data_sql).execute()
                    if resp.data: supabase.table('joana_frequencia').update({"status_presenca": drop_status.value}).eq('id', resp.data[0]['id']).execute()
                    else: supabase.table('joana_frequencia').insert({"id_turma": int(dropdown_turma_chamada.value), "id_aluno": id_aluno, "data": data_sql, "status_presenca": drop_status.value}).execute()
                mostrar_mensagem("Chamada salva/atualizada!")
            except: mostrar_mensagem("Erro.", ft.colors.RED_700)

        def consultar_historico_chamada(e):
            if not dropdown_turma_chamada.value or not input_data_chamada.value: return
            try:
                d_br = input_data_chamada.value
                data_sql = f"{d_br[6:10]}-{d_br[3:5]}-{d_br[0:2]}"
                resp_freq = supabase.table('joana_frequencia').select('id_aluno, status_presenca').eq('id_turma', int(dropdown_turma_chamada.value)).eq('data', data_sql).execute()
                lista_historico_chamada.controls.clear()
                if not resp_freq.data:
                    lista_historico_chamada.controls.append(ft.Text("Nenhuma chamada para este dia.", color="red"))
                else:
                    resp_alunos = {a['id']: a['nome_completo'] for a in supabase.table('joana_alunos').select('id, nome_completo').execute().data}
                    for f in resp_freq.data:
                        cor = "green" if f['status_presenca'] == 'P' else "red" if f['status_presenca'] == 'F' else "orange"
                        lista_historico_chamada.controls.append(ft.Text(f"{resp_alunos.get(f['id_aluno'], 'Desconhecido')} - {f['status_presenca']}", color=cor, weight=ft.FontWeight.BOLD))
                dialog_historico_chamada.open = True; page.update()
            except: pass

        def ao_mudar_turma_notas(e):
            if not dropdown_turma_notas.value: return
            try:
                ids = [i['id_aluno'] for i in supabase.table('joana_turma_alunos').select('id_aluno').eq('id_turma', int(dropdown_turma_notas.value)).execute().data]
                dropdown_aluno_notas.options.clear()
                if ids:
                    for a in supabase.table('joana_alunos').select('id, nome_completo').in_('id', ids).order('nome_completo').execute().data:
                        dropdown_aluno_notas.options.append(ft.dropdown.Option(key=str(a['id']), text=a['nome_completo']))
                dropdown_materia_notas.options.clear()
                for m in supabase.table('joana_materias').select('*').eq('id_turma', int(dropdown_turma_notas.value)).execute().data:
                    dropdown_materia_notas.options.append(ft.dropdown.Option(key=str(m['id']), text=m['nome_materia']))
                page.update()
            except: pass

        def acao_salvar_notas_bimestre(e):
            if not dropdown_aluno_notas.value or not dropdown_materia_notas.value: return
            try:
                id_a = int(dropdown_aluno_notas.value); id_m = int(dropdown_materia_notas.value)
                n1 = float(nota1.value.replace(',', '.')) if nota1.value else 0.0
                n2 = float(nota2.value.replace(',', '.')) if nota2.value else 0.0
                n3 = float(nota3.value.replace(',', '.')) if nota3.value else 0.0
                n4 = float(nota4.value.replace(',', '.')) if nota4.value else 0.0
                media = (n1 + n2 + n3 + n4) / 4
                dados = {"id_aluno": id_a, "id_materia": id_m, "nota1": n1, "nota2": n2, "nota3": n3, "nota4": n4, "media": round(media, 1)}
                
                verifica = supabase.table('joana_notas').select('id').eq('id_aluno', id_a).eq('id_materia', id_m).execute()
                if verifica.data: supabase.table('joana_notas').update(dados).eq('id', verifica.data[0]['id']).execute()
                else: supabase.table('joana_notas').insert(dados).execute()
                
                mostrar_mensagem(f"Salvo! Média: {round(media, 1)}")
                nota1.value = nota2.value = nota3.value = nota4.value = ""; page.update()
            except: mostrar_mensagem("Erro notas.", ft.colors.RED_700)

        id_relatorio_atual = [None]
        def carregar_relatorio_existente(e):
            if not dropdown_aluno_relatorio.value: return
            try:
                resp = supabase.table('joana_relatorios').select('id, texto_relatorio').eq('id_aluno', int(dropdown_aluno_relatorio.value)).execute()
                if resp.data: texto_relatorio.value = resp.data[0]['texto_relatorio']; id_relatorio_atual[0] = resp.data[0]['id']
                else: texto_relatorio.value = ""; id_relatorio_atual[0] = None
                page.update()
            except: pass

        def acao_salvar_relatorio(e):
            if not dropdown_aluno_relatorio.value or not texto_relatorio.value: return
            try:
                dados = {"id_aluno": int(dropdown_aluno_relatorio.value), "texto_relatorio": texto_relatorio.value, "data_criacao": datetime.now().strftime("%d/%m/%Y")}
                if id_relatorio_atual[0]: supabase.table('joana_relatorios').update(dados).eq('id', id_relatorio_atual[0]).execute()
                else: id_relatorio_atual[0] = supabase.table('joana_relatorios').insert(dados).execute().data[0]['id']
                mostrar_mensagem("Relatório salvo!"); page.update()
            except: mostrar_mensagem("Erro relatório.", ft.colors.RED_700)

        def acao_gerar_pdf_relatorio(e):
            if not dropdown_aluno_relatorio.value: return
            nome_aluno = next(opt.text for opt in dropdown_aluno_relatorio.options if opt.key == dropdown_aluno_relatorio.value)
            gerar_pdf_relatorio(nome_aluno, texto_relatorio.value)

        def carregar_boletim_aluno(e):
            if not dropdown_aluno_boletim.value: return
            try:
                lista_boletim_notas.controls.clear()
                resp_notas = supabase.table('joana_notas').select('*').eq('id_aluno', int(dropdown_aluno_boletim.value)).execute()
                mapa_materias = {m['id']: m['nome_materia'] for m in supabase.table('joana_materias').select('id, nome_materia').execute().data}
                dados_pdf = []
                if not resp_notas.data: lista_boletim_notas.controls.append(ft.Text("Nenhuma nota.", color="red"))
                else:
                    for n in resp_notas.data:
                        nome_mat = mapa_materias.get(n['id_materia'], 'Desconhecida')
                        dados_pdf.append({'materia': nome_mat, 'n1': n['nota1'], 'n2': n['nota2'], 'n3': n['nota3'], 'n4': n['nota4'], 'media': n['media']})
                        lista_boletim_notas.controls.append(ft.Card(content=ft.Container(padding=10, content=ft.Column([ft.Text(nome_mat, weight=ft.FontWeight.BOLD, color=ROXO_FORTE, size=16), ft.Row([ft.Text(f"1º: {n['nota1']}"), ft.Text(f"2º: {n['nota2']}"), ft.Text(f"3º: {n['nota3']}"), ft.Text(f"4º: {n['nota4']}")], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), ft.Text(f"Média: {n['media']}", weight=ft.FontWeight.BOLD, color="green" if n['media'] >= 6 else "red")]))))
                nome_aluno = next(opt.text for opt in dropdown_aluno_boletim.options if opt.key == str(dropdown_aluno_boletim.value))
                btn_gerar_pdf_boletim.on_click = lambda e: gerar_pdf_boletim(nome_aluno, dados_pdf); page.update()
            except: pass

        input_nome_turma = ft.TextField(label="Nome", border_color=ROXO_FORTE, bgcolor=BRANCO)
        input_horario_turma = ft.TextField(label="Horários", border_color=ROXO_FORTE, bgcolor=BRANCO)
        input_dias_turma = ft.TextField(label="Dias", border_color=ROXO_FORTE, bgcolor=BRANCO)
        tela_turmas = ft.Container(content=ft.Column([ft.Text("Turmas", size=24, weight=ft.FontWeight.BOLD, color=ROXO_FORTE), input_nome_turma, input_horario_turma, input_dias_turma, ft.ElevatedButton("Nova Turma", bgcolor=ROXO_FORTE, color=BRANCO, width=300, on_click=acao_salvar_turma), ft.Divider(), lista_turmas_edit], horizontal_alignment=ft.CrossAxisAlignment.CENTER), padding=20, visible=False)

        dropdown_turma_aluno = ft.Dropdown(label="Vincular à Turma", border_color=ROXO_FORTE, bgcolor=BRANCO)
        input_nome_aluno = ft.TextField(label="Nome Completo", border_color=ROXO_FORTE, bgcolor=BRANCO)
        input_mae_aluno = ft.TextField(label="Nome da Mãe", border_color=ROXO_FORTE, bgcolor=BRANCO) 
        input_nasc_aluno = ft.TextField(label="Nascimento", border_color=ROXO_FORTE, bgcolor=BRANCO, on_blur=formatar_data_ao_sair)
        input_end_aluno = ft.TextField(label="Endereço", border_color=ROXO_FORTE, bgcolor=BRANCO)
        input_tel_aluno = ft.TextField(label="Telefone", border_color=ROXO_FORTE, bgcolor=BRANCO, on_blur=formatar_telefone_ao_sair)
        preview_foto_aluno = ft.CircleAvatar(radius=40, bgcolor=ROXO_CLARO, content=ft.Icon(ft.icons.PERSON, color=BRANCO, size=40))
        tela_alunos = ft.Container(content=ft.Column([ft.Text("Alunos", size=24, weight=ft.FontWeight.BOLD, color=ROXO_FORTE), ft.Stack([preview_foto_aluno, ft.Container(content=ft.Icon(ft.icons.CAMERA_ALT, color=BRANCO, size=15), bgcolor=ROXO_FORTE, shape=ft.BoxShape.CIRCLE, padding=6, right=0, bottom=0, on_click=lambda _: picker_aluno.pick_files())]), dropdown_turma_aluno, input_nome_aluno, input_mae_aluno, input_nasc_aluno, input_end_aluno, input_tel_aluno, ft.ElevatedButton("Salvar Aluno", bgcolor=ROXO_FORTE, color=BRANCO, width=300, on_click=acao_salvar_aluno), ft.Divider(), lista_alunos_edit], horizontal_alignment=ft.CrossAxisAlignment.CENTER), padding=20, visible=False)

        dropdown_turma_materia = ft.Dropdown(label="Turma da Matéria", border_color=ROXO_FORTE, bgcolor=BRANCO)
        input_nome_materia = ft.TextField(label="Nome da Matéria", border_color=ROXO_FORTE, bgcolor=BRANCO)
        tela_materias = ft.Container(content=ft.Column([ft.Text("Matérias", size=24, weight=ft.FontWeight.BOLD, color=ROXO_FORTE), dropdown_turma_materia, input_nome_materia, ft.ElevatedButton("Salvar Matéria", bgcolor=ROXO_FORTE, color=BRANCO, width=300, on_click=acao_salvar_materia), ft.Divider(), ft.Text("Cadastradas"), lista_materias_edit], horizontal_alignment=ft.CrossAxisAlignment.CENTER), padding=20, visible=False)

        dropdown_turma_chamada = ft.Dropdown(label="Selecione a Turma", border_color=ROXO_FORTE, bgcolor=BRANCO, on_change=ao_mudar_turma_chamada)
        input_data_chamada = ft.TextField(label="Data", border_color=ROXO_FORTE, bgcolor=BRANCO, value=datetime.now().strftime("%d/%m/%Y"))
        lista_chamada_alunos = ft.Column(scroll=ft.ScrollMode.AUTO, height=300, spacing=10)
        tela_chamada = ft.Container(content=ft.Column([ft.Text("Chamada", size=24, weight=ft.FontWeight.BOLD, color=ROXO_FORTE), ft.Row([dropdown_turma_chamada, input_data_chamada], alignment=ft.MainAxisAlignment.CENTER), ft.ElevatedButton("Ver Histórico", icon=ft.icons.HISTORY, on_click=consultar_historico_chamada), ft.Divider(), lista_chamada_alunos, ft.ElevatedButton("Salvar Chamada", bgcolor="green700", color=BRANCO, width=300, on_click=acao_salvar_frequencia)], horizontal_alignment=ft.CrossAxisAlignment.CENTER), padding=20, visible=False)

        dropdown_turma_notas = ft.Dropdown(label="1. Turma", border_color=ROXO_FORTE, bgcolor=BRANCO, on_change=ao_mudar_turma_notas)
        dropdown_materia_notas = ft.Dropdown(label="2. Matéria", border_color=ROXO_FORTE, bgcolor=BRANCO)
        dropdown_aluno_notas = ft.Dropdown(label="3. Aluno", border_color=ROXO_FORTE, bgcolor=BRANCO)
        nota1 = ft.TextField(label="1º Bim", width=80, border_color=ROXO_FORTE); nota2 = ft.TextField(label="2º Bim", width=80, border_color=ROXO_FORTE); nota3 = ft.TextField(label="3º Bim", width=80, border_color=ROXO_FORTE); nota4 = ft.TextField(label="4º Bim", width=80, border_color=ROXO_FORTE)
        tela_notas = ft.Container(content=ft.Column([ft.Text("Notas", size=24, weight=ft.FontWeight.BOLD, color=ROXO_FORTE), dropdown_turma_notas, dropdown_materia_notas, dropdown_aluno_notas, ft.Row([nota1, nota2, nota3, nota4], alignment=ft.MainAxisAlignment.CENTER), ft.ElevatedButton("Salvar Notas", bgcolor=ROXO_FORTE, color=BRANCO, width=300, on_click=acao_salvar_notas_bimestre)], horizontal_alignment=ft.CrossAxisAlignment.CENTER), padding=20, visible=False)

        dropdown_aluno_relatorio = ft.Dropdown(label="Selecione o Aluno", border_color=ROXO_FORTE, bgcolor=BRANCO, on_change=carregar_relatorio_existente)
        texto_relatorio = ft.TextField(label="Texto...", border_color=ROXO_FORTE, bgcolor=BRANCO, multiline=True, min_lines=5)
        tela_relatorios = ft.Container(content=ft.Column([ft.Text("Relatórios", size=24, weight=ft.FontWeight.BOLD, color=ROXO_FORTE), dropdown_aluno_relatorio, texto_relatorio, ft.ElevatedButton("Salvar no Banco", bgcolor=ROXO_FORTE, color=BRANCO, width=300, on_click=acao_salvar_relatorio), ft.Divider(), ft.ElevatedButton("Gerar PDF", bgcolor="red700", color=BRANCO, width=300, icon=ft.icons.PICTURE_AS_PDF, on_click=acao_gerar_pdf_relatorio)], horizontal_alignment=ft.CrossAxisAlignment.CENTER), padding=20, visible=False)

        dropdown_aluno_boletim = ft.Dropdown(label="Selecione o Aluno", border_color=ROXO_FORTE, bgcolor=BRANCO, on_change=carregar_boletim_aluno)
        lista_boletim_notas = ft.Column(scroll=ft.ScrollMode.AUTO, height=300, spacing=10)
        btn_gerar_pdf_boletim = ft.ElevatedButton("Gerar PDF", bgcolor="red700", color=BRANCO, width=300, icon=ft.icons.PICTURE_AS_PDF)
        tela_boletim = ft.Container(content=ft.Column([ft.Text("Boletins", size=24, weight=ft.FontWeight.BOLD, color=ROXO_FORTE), dropdown_aluno_boletim, lista_boletim_notas, ft.Divider(), btn_gerar_pdf_boletim], horizontal_alignment=ft.CrossAxisAlignment.CENTER), padding=20, visible=False)

        tela_config = ft.Container(content=ft.Column([ft.Text("Configurações", size=24, weight=ft.FontWeight.BOLD, color=ROXO_FORTE), ft.Icon(ft.icons.SETTINGS, size=80, color=ROXO_CLARO), ft.Text("Versão Android Box", color="black", weight=ft.FontWeight.BOLD), ft.ElevatedButton("Sincronizar", icon=ft.icons.SYNC, bgcolor=ROXO_FORTE, color=BRANCO, width=300, on_click=lambda e: carregar_dados_gerais() or mostrar_mensagem("OK!"))], horizontal_alignment=ft.CrossAxisAlignment.CENTER), padding=20, visible=False)

        telas = {"home": None, "turmas": tela_turmas, "alunos": tela_alunos, "materias": tela_materias, "chamada": tela_chamada, "notas": tela_notas, "relatorios": tela_relatorios, "boletim": tela_boletim, "config": tela_config}

        def abrir_tela(nome_tela):
            carregar_dados_gerais()
            for nome, container in telas.items():
                if container: container.visible = (nome == nome_tela)
            page.update()

        def criar_atalho(icone, texto, acao, cor_fundo=BRANCO, cor_icone=ROXO_FORTE):
            return ft.Container(content=ft.Column([ft.Icon(name=icone, size=40, color=cor_icone), ft.Text(texto, size=16, weight=ft.FontWeight.BOLD, color=cor_icone)], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5), bgcolor=cor_fundo, width=150, height=120, border_radius=15, border=ft.border.all(1, ROXO_CLARO), shadow=ft.BoxShadow(spread_radius=1, blur_radius=5, color=ft.colors.BLACK12, offset=ft.Offset(0, 2)), ink=True, on_click=lambda e: abrir_tela(acao))

        foto_salva = page.client_storage.get("foto_joana")
        avatar_joana = ft.CircleAvatar(radius=50, bgcolor=ROXO_FORTE, background_image_url=foto_salva if foto_salva else None, content=None if foto_salva else ft.Icon(ft.icons.FACE_RETOUCHING_NATURAL, size=50, color=BRANCO))

        telas["home"] = ft.Container(content=ft.Column([
            ft.Container(content=ft.Column([ft.Stack([avatar_joana, ft.Container(content=ft.Icon(ft.icons.CAMERA_ALT, color=BRANCO, size=15), bgcolor=ROXO_CLARO, shape=ft.BoxShape.CIRCLE, padding=6, right=0, bottom=0, on_click=lambda _: picker_joana.pick_files())]), ft.Text("Diário da Joana", size=26, weight=ft.FontWeight.BOLD, color=ROXO_FORTE)], horizontal_alignment=ft.CrossAxisAlignment.CENTER), padding=ft.padding.only(top=20, bottom=20)),
            ft.Divider(),
            ft.Row([criar_atalho(ft.icons.FACT_CHECK, "Chamada", "chamada", "#E1BEE7", ROXO_FORTE), criar_atalho(ft.icons.ASSESSMENT, "Boletins", "boletim", "#E1BEE7", ROXO_FORTE)], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([criar_atalho(ft.icons.CLASS_, "Turmas", "turmas"), criar_atalho(ft.icons.PEOPLE, "Alunos", "alunos")], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([criar_atalho(ft.icons.EDIT_DOCUMENT, "Notas", "notas"), criar_atalho(ft.icons.MENU_BOOK, "Matérias", "materias")], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([criar_atalho(ft.icons.PICTURE_AS_PDF, "Relatórios", "relatorios"), criar_atalho(ft.icons.SETTINGS, "Config.", "config")], alignment=ft.MainAxisAlignment.CENTER),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER), visible=True)

        def mudar_aba_inferior(index):
            if index == 0: abrir_tela("home")
            elif index == 1: abrir_tela("turmas")
            elif index == 2: abrir_tela("alunos")
            page.update()

        barra_navegacao = ft.Container(content=ft.Row([
            ft.Container(content=ft.Column([ft.Icon(name=ft.icons.HOME, color=BRANCO, size=26), ft.Text("Início", color=BRANCO, size=12, weight=ft.FontWeight.BOLD)], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2), expand=True, ink=True, on_click=lambda e: mudar_aba_inferior(0)), 
            ft.Container(content=ft.Column([ft.Icon(name=ft.icons.CLASS_OUTLINED, color=BRANCO, size=26), ft.Text("Turmas", color=BRANCO, size=12, weight=ft.FontWeight.BOLD)], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2), expand=True, ink=True, on_click=lambda e: mudar_aba_inferior(1)), 
            ft.Container(content=ft.Column([ft.Icon(name=ft.icons.PEOPLE, color=BRANCO, size=26), ft.Text("Alunos", color=BRANCO, size=12, weight=ft.FontWeight.BOLD)], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2), expand=True, ink=True, on_click=lambda e: mudar_aba_inferior(2))
        ], alignment=ft.MainAxisAlignment.SPACE_AROUND), bgcolor=ROXO_FORTE, height=65, padding=ft.padding.only(top=5, bottom=5))

        topo = ft.Container(content=ft.Text("App da Professora", color=BRANCO, weight=ft.FontWeight.BOLD, size=18), bgcolor=ROXO_FORTE, padding=15, alignment=ft.alignment.center)
        conteudo_principal = ft.Container(content=ft.Column([telas["home"], tela_turmas, tela_alunos, tela_materias, tela_chamada, tela_notas, tela_relatorios, tela_boletim, tela_config], expand=True, scroll=ft.ScrollMode.AUTO), expand=True)
        page.add(ft.Column([topo, conteudo_principal, barra_navegacao], expand=True, spacing=0))
        carregar_dados_gerais()

    # SE QUALQUER COISA DER ERRADO, A TELA FICA VERMELHA E MOSTRA O ERRO AQUI!
    except Exception as e:
        erro_completo = traceback.format_exc()
        page.scroll = ft.ScrollMode.AUTO
        page.add(
            ft.Column([
                ft.Icon(ft.icons.BUG_REPORT, color="red", size=80),
                ft.Text("Eita, Ap! O Android barrou!", color="red", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Mande todo esse texto vermelho pra Lumi resolver:", color="black", weight="bold"),
                ft.TextField(value=erro_completo, multiline=True, read_only=True, color="red", border_color="red", min_lines=20)
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
        page.update()

ft.app(target=main)
