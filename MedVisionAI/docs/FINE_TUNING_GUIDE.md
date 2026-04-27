# 🏥 Fine-Tuning YOLOv8 para Instrumentos Cirúrgicos

Guia completo para treinar o modelo de detecção de instrumentos cirúrgicos usando o dataset GynSurge.

---

## 📋 Pré-requisitos

### 1. Hardware Recomendado

**Opção A: GPU Local (Melhor)**
- NVIDIA GPU com 6GB+ VRAM (GTX 1060, RTX 2060+)
- 16GB+ RAM
- 50GB espaço em disco

**Opção B: Google Colab (Grátis!) ⭐ RECOMENDADO**
- GPU Tesla T4 gratuita
- Sem necessidade de instalação local
- Ver: `notebooks/train_colab.ipynb`

**Opção C: CPU (Muito Lento)**
- Use apenas para testes com 10-20 épocas

### 2. Dataset GynSurge

**Download:**
```bash
# Manual: https://ftp.itec.aau.at/datasets/GynSurge/

# Ou via wget:
cd C:\dev\TechChallengeF04\datasets
wget -r -np -nH --cut-dirs=2 https://ftp.itec.aau.at/datasets/GynSurge/
```

**Estrutura Esperada:**
```
C:\dev\TechChallengeF04\datasets\gynsurge\
├── images/
│   ├── frame_0001.jpg
│   ├── frame_0002.jpg
│   └── ...
├── annotations/
│   ├── frame_0001.json  (ou .xml)
│   └── ...
└── README.txt
```

---

## 🚀 Processo de Fine-Tuning

### Passo 1: Preparar Dataset

Converte anotações GynSurge para formato YOLO:

```bash
cd C:\dev\TechChallengeF04\medvision-ai
.\backend\venv\Scripts\activate

python scripts\prepare_gynsurge_dataset.py
```

**⚠️ IMPORTANTE:** Ajuste o script conforme formato real das anotações!
- Se forem JSON: adapte `process_annotation()`
- Se forem XML (PASCAL VOC): use biblioteca diferente
- Se forem máscaras PNG: use `mask_to_bbox()`

**Saída:**
```
datasets/gynsurge_yolo/
├── images/
│   ├── train/  (70% das imagens)
│   ├── val/    (20%)
│   └── test/   (10%)
├── labels/
│   ├── train/  (.txt no formato YOLO)
│   ├── val/
│   └── test/
└── data.yaml   (configuração)
```

### Passo 2: Verificar data.yaml

```yaml
# datasets/gynsurge_yolo/data.yaml

path: C:/dev/TechChallengeF04/medvision-ai/datasets/gynsurge_yolo
train: images/train
val: images/val
test: images/test

nc: 10  # número de classes
names:
  - needle-holder
  - needle
  - irrigator
  - needle-holder-head
  - needle-thread
  - scissors
  - grasper
  - clip-applier
  - hook
  - other
```

### Passo 3: Treinar Modelo

#### 3.1 Local (se tiver GPU)

```bash
python scripts\train_yolov8_gynsurge.py
```

**Menu Interativo:**
```
Tamanho do modelo: n  (nano - mais rápido)
Épocas: 100
Batch size: 16  (reduza para 8 se ficar sem memória)
```

#### 3.2 Google Colab (Recomendado)

1. Abra: `notebooks/train_colab.ipynb`
2. Runtime > Change runtime type > **GPU** (T4)
3. Execute todas as células
4. Baixe `best.pt` ao final

### Passo 4: Integrar Modelo Treinado

```bash
# Copie o modelo treinado
copy runs\train\gynsurge_yolov8n\weights\best.pt backend\models_weights\yolov8_gyneco.pt

# Reinicie o backend
# O sistema detectará automaticamente o novo modelo!
```

---

## 📊 Monitoramento do Treinamento

Durante o treinamento, você verá:

```
Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
1/100      3.5G      1.234      0.567      1.123         45        640
...
```

**Métricas Importantes:**
- **box_loss**: Erro de localização (deve diminuir)
- **cls_loss**: Erro de classificação (deve diminuir)
- **mAP50**: Precisão média @ IoU 0.5 (deve aumentar)
- **mAP50-95**: Precisão média @ IoU 0.5-0.95 (mais rigoroso)

**Visualizações Geradas:**
```
runs/train/gynsurge_yolov8n/
├── weights/
│   ├── best.pt      ⭐ Use este!
│   └── last.pt
├── results.png      (gráficos de loss/métricas)
├── confusion_matrix.png
├── PR_curve.png
└── val_batch0_pred.jpg  (predições visualizadas)
```

---

## 🎯 Hiperparâmetros Recomendados

### Para Dataset Pequeno (<1000 imagens)

```python
epochs = 50
batch_size = 8
patience = 20
lr0 = 0.0005  # Learning rate menor
```

### Para Dataset Médio (1000-5000 imagens)

```python
epochs = 100
batch_size = 16
patience = 50
lr0 = 0.001
```

### Para Dataset Grande (>5000 imagens)

```python
epochs = 150-300
batch_size = 32 (se tiver VRAM)
patience = 100
lr0 = 0.001
```

---

## ⚡ Dicas de Otimização

### 1. Reduzir Uso de Memória

```python
batch_size = 4      # Menor batch
imgsz = 416        # Imagens menores (padrão: 640)
cache = False      # Não cacheia imagens
workers = 4        # Menos workers
```

### 2. Acelerar Treinamento

```python
cache = 'ram'      # Cacheia em RAM (se tiver >16GB)
amp = True         # Mixed precision
workers = 8        # Mais workers (se tiver CPU potente)
```

### 3. Melhorar Precisão

```python
model_size = 'm'   # Modelo maior (medium)
epochs = 200       # Mais épocas
augment = True     # Data augmentation
mosaic = 1.0       # Mosaic augmentation
```

---

## 🧪 Validação e Testes

### Validar Modelo Treinado

```bash
python -c "
from ultralytics import YOLO
model = YOLO('backend/models_weights/yolov8_gyneco.pt')
results = model.val(split='test')
print(f'mAP50: {results.box.map50:.4f}')
print(f'mAP50-95: {results.box.map:.4f}')
"
```

### Testar em Imagem Individual

```bash
python -c "
from ultralytics import YOLO
model = YOLO('backend/models_weights/yolov8_gyneco.pt')
results = model.predict('path/to/test_image.jpg', save=True)
print(f'Detecções: {len(results[0].boxes)}')
"
```

### Testar em Vídeo

```bash
python -c "
from ultralytics import YOLO
model = YOLO('backend/models_weights/yolov8_gyneco.pt')
results = model.predict('path/to/surgery_video.mp4', save=True)
"
```

---

## 📈 Interpretando Resultados

### Bons Resultados
- ✅ mAP50 > 0.7 (70%+)
- ✅ Loss convergindo (não pulando)
- ✅ Detecções visuais corretas

### Problemas Comuns

**1. Overfitting**
- Sintomas: Train loss baixo, val loss alto
- Solução: Mais data augmentation, dropout, early stopping

**2. Underfitting**
- Sintomas: Ambos loss altos
- Solução: Modelo maior, mais épocas, learning rate ajustado

**3. Classes Desbalanceadas**
- Sintomas: Algumas classes não detectadas
- Solução: Weighted loss, mais exemplos, data augmentation

---

## 🔧 Troubleshooting

### CUDA Out of Memory

```python
batch_size = 4      # Menor
imgsz = 416        # Imagens menores
cache = False
```

### Treinamento Muito Lento (CPU)

**Solução:** Use Google Colab com GPU!

### Labels Incorretos

```bash
# Visualize labels
from ultralytics.utils import check_dataset
check_dataset('datasets/gynsurge_yolo/data.yaml')
```

### Modelo Não Detecta Nada

1. Verifique se labels estão corretos
2. Aumente épocas
3. Ajuste confidence threshold no código

---

## 📚 Recursos Adicionais

- [YOLOv8 Docs](https://docs.ultralytics.com/)
- [GynSurge Dataset Paper](https://ftp.itec.aau.at/datasets/GynSurge/)
- [Transfer Learning Guide](https://docs.ultralytics.com/modes/train/#resuming-interrupted-trainings)

---

## 🎓 Google Colab Notebook

```python
# notebooks/train_colab.ipynb

# 1. Setup
!pip install ultralytics
from google.colab import drive
drive.mount('/content/drive')

# 2. Upload Dataset
# Via Google Drive ou wget

# 3. Train
from ultralytics import YOLO
model = YOLO('yolov8n.pt')
results = model.train(
    data='/content/data.yaml',
    epochs=100,
    imgsz=640,
    batch=16,
    device=0
)

# 4. Download Modelo
from google.colab import files
files.download('runs/train/exp/weights/best.pt')
```

---

## ✅ Checklist

- [ ] Dataset GynSurge baixado
- [ ] Annotations convertidas para YOLO
- [ ] data.yaml configurado
- [ ] Modelo treinado (mAP50 > 0.5)
- [ ] best.pt copiado para `models_weights/`
- [ ] Backend reiniciado
- [ ] Testado em vídeo cirúrgico real
- [ ] Bounding boxes aparecem na interface

---

**🎉 BOA SORTE COM O TREINAMENTO!**
