from pathlib import Path

path = Path(__file__).with_name('index.html')
original = path.read_text(encoding='utf-8')
correcoes = {
    'top:130px;left:100px;right:100px;color:#fff;font:bold 44px': 'top:286px;left:160px;right:165px;color:#fff;font:bold 44px',
    'bottom:150px;left:100px;right:100px;color:#fff;font:30px': 'bottom:277px;left:160px;right:165px;color:#fff;font:30px',
}
corrigido = original
for antes, depois in correcoes.items():
    if corrigido.count(antes) != 1:
        raise ValueError(f'Texto da abertura inesperado: {antes}')
    corrigido = corrigido.replace(antes, depois, 1)
path.write_text(corrigido, encoding='utf-8')
path.with_name('previa-corrigida.html').write_text(corrigido, encoding='utf-8')
