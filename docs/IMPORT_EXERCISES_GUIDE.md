# 📥 Guia de Importação de Exercícios

Este guia cobre dois formatos de importação:
1. **Formato Padrão** - CSV com colunas name, muscle_group, equipment, description, image_path
2. **Formato Português** - CSV com pares de colunas por grupo muscular (formato do Google Sheets)

---

## 🇵🇹 FORMATO PORTUGUÊS (Recomendado para Google Sheets)

### ✅ Como Funciona

Seu CSV tem exercícios organizados em **pares de colunas** por grupo muscular:
- Cada grupo muscular tem 2 colunas: Nome do Exercício + Nome do Grupo
- Exemplo: `Exercício, Peito, Exercício, Pernas, Exercício, Ombros...`
- Os exercícios aparecem nas linhas abaixo de cada grupo

### 📊 Exemplo de Estrutura

```csv
Exercício,Peito,Exercício,Pernas,Exercicio,Ombros,Exercicio,Costas
Supino,,Agachamento,,Press Ombros,,Pull Down,
Flexões,,Leg Press,,Elevação Lateral,,Remada,
Cross Over,,Lunge,,Press Militar,,Pull Over,
```

### 🚀 Importação Rápida

```bash
# 1. Coloque seu CSV na pasta Imports/
cp meu_arquivo.csv Imports/exercicios.csv

# 2. Execute o script
./import-exercises-pt.sh

# Ou especifique o arquivo
./import-exercises-pt.sh Imports/meu_arquivo.csv
```

### 🎯 Grupos Musculares Suportados

O script **mapeia automaticamente** de Português → Inglês:
- `Peito` → Chest
- `Pernas` → Legs
- `Ombros` → Shoulders
- `Costas` → Back
- `Triceps` → Triceps
- `Biceps` → Biceps
- `Core` → Abs
- `Cardio` → Cardio
- `Trapézio` → Back
- `Glúteos` → Glutes

### 📝 O Que o Script Faz

1. ✅ Identifica automaticamente os pares de colunas
2. ✅ Extrai todos os exercícios de todas as linhas
3. ✅ Mapeia grupos musculares de PT → EN
4. ✅ Evita duplicatas
5. ✅ Importa para o primeiro Personal Trainer ou usuário especificado

### 💡 Exemplo de Saída

```
============================================================
IMPORT EXERCISES FROM PORTUGUESE CSV
============================================================

📋 Importing exercises for user: Nuno Oliveira (nuno@isfit.com)

📊 Found 10 muscle group columns:
   - Column 0: Peito → Chest
   - Column 2: Pernas → Legs
   - Column 4: Ombros → Shoulders
   ...

📝 Found 101 total exercises in CSV

✅ Created 'Supino' (Chest)
✅ Created 'Agachamento c/ Barra' (Legs)
✅ Created 'Press de Ombros Halteres' (Shoulders)
...
⏭️  'Cross Over' (Shoulders) already exists, skipping

============================================================
✅ Import completed!
   Imported: 99
   Skipped:  2
   Errors:   0
============================================================
```

---

## 🌍 FORMATO PADRÃO (CSV Internacional)

### 1️⃣ Preparar o CSV

**Opção A: Exportar do Google Sheets**

1. Abra sua planilha no Google Sheets
2. **File** → **Download** → **Comma-separated values (.csv)**
3. Salve como `meus_exercicios.csv` na raiz do projeto

**Opção B: Usar o Template**

```bash
# Já existe um template pronto:
exercises_template.csv
```

### 2️⃣ Preparar as Imagens (Opcional)

Se você tem imagens dos exercícios:

1. **Crie uma pasta** para as imagens:
   ```bash
   mkdir exercise_images
   ```

2. **Baixe as imagens** do Google Sheets e coloque nesta pasta:
   ```
   exercise_images/
   ├── bench_press.jpg
   ├── squat.jpg
   ├── deadlift.jpg
   └── ...
   ```

3. **No CSV**, adicione o caminho das imagens:
   ```csv
   name,muscle_group,equipment,description,image_path
   Bench Press,Chest,Barbell,Classic exercise,exercise_images/bench_press.jpg
   Squat,Legs,Barbell,Compound exercise,exercise_images/squat.jpg
   ```

### 3️⃣ Importar!

```bash
./import-exercises.sh meus_exercicios.csv
```

**Pronto!** ✅ Os exercícios serão importados com imagens!

---

## 📋 Formato do CSV

### Colunas Obrigatórias:
- `name` - Nome do exercício
- `muscle_group` - Grupo muscular

### Colunas Opcionais:
- `equipment` - Equipamento necessário
- `description` - Descrição do exercício
- `image_path` - Caminho para a imagem

### Grupos Musculares Válidos:
- `Chest` (Peito)
- `Back` (Costas)
- `Shoulders` (Ombros)
- `Biceps` (Bíceps)
- `Triceps` (Tríceps)
- `Legs` (Pernas)
- `Glutes` (Glúteos)
- `Abs` (Abdômen)
- `Cardio` (Cardio)

### Exemplo de CSV:

```csv
name,muscle_group,equipment,description,image_path
Bench Press,Chest,Barbell,Classic chest exercise,images/bench_press.jpg
Squat,Legs,Barbell,Builds leg strength,images/squat.jpg
Pull Up,Back,Bodyweight,Great for lats,images/pullup.jpg
Plank,Abs,Bodyweight,Core stability,
Running,Cardio,Bodyweight,Cardio endurance,
```

---

## 🖼️ Sobre as Imagens

### Como Baixar Imagens do Google Sheets?

1. **Clique com botão direito** na imagem
2. **"Save image as..."** ou **"Salvar imagem como..."**
3. Salve na pasta `exercise_images/`
4. Renomeie para algo simples (ex: `bench_press.jpg`)

### Formatos Suportados:
- ✅ `.jpg` / `.jpeg`
- ✅ `.png`
- ✅ `.gif`

### Tamanho Recomendado:
- Máximo: 5MB por imagem
- Resolução: 800x600 ou similar

---

## 🚀 Exemplos de Uso

### Exemplo 1: Importar Sem Imagens
```bash
./import-exercises.sh exercises_template.csv
```

### Exemplo 2: Importar Com Imagens
```bash
# 1. Criar pasta
mkdir exercise_images

# 2. Baixar imagens do Google Sheets para exercise_images/

# 3. Editar CSV com caminhos das imagens
nano meus_exercicios.csv

# 4. Importar
./import-exercises.sh meus_exercicios.csv
```

### Exemplo 3: Importar Para Usuário Específico
```bash
# Primeiro, pegue o ID do usuário
./list-users.sh

# Depois importe
./import-exercises.sh meus_exercicios.csv --user-id UUID-DO-USUARIO
```

---

## 📊 O Que o Script Faz

1. ✅ Valida o CSV
2. ✅ Verifica grupos musculares
3. ✅ Copia imagens para `/app/uploads`
4. ✅ Cria exercícios no banco de dados
5. ✅ Associa imagens aos exercícios
6. ✅ Evita duplicatas (pula se já existir)
7. ✅ Mostra progresso em tempo real

---

## 🎯 Saída do Script

```
====================================================================
IMPORT EXERCISES FROM CSV
====================================================================

📋 Importing exercises for user: João Silva (joao@email.com)

✅ Row 2: Created 'Bench Press' (Chest)
   📷 Image uploaded: abc-123-def.jpg
✅ Row 3: Created 'Squat' (Legs)
   📷 Image uploaded: def-456-ghi.jpg
⏭️  Row 4: 'Deadlift' already exists, skipping
✅ Row 5: Created 'Pull Up' (Back)

====================================================================
✅ Import completed!
   Imported: 3
   Skipped:  1
   Errors:   0
====================================================================
```

---

## 🐛 Troubleshooting

### Erro: "gym_backend container is not running"
```bash
bash start-containers.sh
# ou
podman ps -a  # verificar se containers estão rodando
```

### Erro: "CSV file not found"
Certifique-se de estar na raiz do projeto:
```bash
cd /home/aamarques/Gym/GymTracker/

# Para formato português, verifique se o arquivo está em Imports/
ls Imports/
```

### Qual Script Usar?

**Use `import-exercises-pt.sh` se:**
- Seu CSV veio do Google Sheets com exercícios em colunas por grupo muscular
- Os grupos musculares estão em português
- O CSV tem estrutura de pares de colunas

**Use `import-exercises.sh` se:**
- Seu CSV tem formato padrão com colunas: name, muscle_group, equipment, etc.
- Você quer incluir imagens dos exercícios
- Os grupos musculares já estão em inglês

### Erro: "Invalid muscle group"
Use um dos grupos válidos:
- Chest, Back, Shoulders, Biceps, Triceps, Legs, Glutes, Abs, Cardio

### Erro: "Image not found"
Verifique se o caminho da imagem está correto:
```bash
ls exercise_images/
```

### Imagens não aparecem no app
Verifique se as imagens foram copiadas:
```bash
podman exec gym_backend ls /app/uploads/
```

---

## 💡 Dicas

### Preparando o Google Sheets

1. **Organize as colunas** exatamente como no template
2. **Use grupos musculares em inglês** (Chest, Legs, etc.)
3. **Exporte como CSV** (não Excel!)
4. **Baixe as imagens** antes de importar

### Testando Primeiro

Teste com poucos exercícios primeiro:
```bash
# Crie um CSV só com 3 exercícios
./import-exercises.sh test.csv
```

Se funcionar, importe o resto!

---

## 📚 Arquivos de Importação

### Scripts Disponíveis

1. **`import-exercises-pt.sh`** - Para CSV em formato português (colunas pareadas)
   - Usa: `backend/import_exercises_pt.py`
   - Para: CSV exportado do Google Sheets com estrutura de colunas por grupo muscular

2. **`import-exercises.sh`** - Para CSV em formato padrão
   - Usa: `backend/import_exercises.py`
   - Para: CSV com colunas: name, muscle_group, equipment, description, image_path

### Outros Arquivos

- `exercises_template.csv` - Template de exemplo (formato padrão)
- `Imports/` - Pasta recomendada para seus arquivos CSV
- `exercise_images/` - Pasta para suas imagens (você cria)

---

## ✨ Próximos Passos

Depois de importar:
1. ✅ Acesse http://localhost:8080
2. ✅ Faça login como Personal Trainer
3. ✅ Vá na aba **Exercises**
4. ✅ Veja todos os exercícios importados com imagens!

Sucesso! 🎉
