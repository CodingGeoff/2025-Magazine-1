import os
import random
import string
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
import pyperclip
import hashlib

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
HASH_FILE = 'static/file_hashes.txt'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(HASH_FILE):
    open(HASH_FILE, 'w').close()

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 更多有意义的单词用于生成正确密钥
MEANINGFUL_WORDS = [
    "sunshine", "rainbow", "ocean", "mountain", "forest",
    "star", "moon", "flower", "butterfly", "cloud",
    "river", "island", "valley", "desert", "canyon",
    "meadow", "glacier", "volcano", "lake", "waterfall",
    "wind", "fire", "earth", "air", "snow",
    "ice", "mist", "dew", "frost", "hail",
    "thunder", "lightning", "storm", "hurricane", "tornado",
    "drizzle", "shower", "blizzard", "fog", "smog",
    "planet", "comet", "asteroid", "galaxy", "nebula",
    "universe", "constellation", "meteor", "meteorite",
    "tree", "leaf", "branch", "root", "bark",
    "grass", "weed", "vine", "fern", "moss",
    "bamboo", "pinecone", "acorn", "seed", "bud",
    "blossom", "lion", "tiger", "bear", "wolf",
    "fox", "deer", "rabbit", "squirrel", "bird",
    "eagle", "dove", "sparrow", "owl", "fish",
    "shark", "whale", "dolphin", "turtle", "snake",
    "lizard", "frog", "toad", "bee", "ant",
    "spider", "worm", "love", "joy", "happiness",
    "peace", "hope", "faith", "courage", "confidence",
    "pride", "excitement", "enthusiasm", "contentment", "gratitude",
    "kindness", "compassion", "empathy", "friendship", "loyalty",
    "trust", "sadness", "grief", "anger", "hate",
    "fear", "anxiety", "worry", "stress", "loneliness",
    "envy", "jealousy", "regret", "guilt", "shame",
    "wisdom", "intelligence", "creativity", "perseverance", "patience",
    "tolerance", "generosity", "honesty", "integrity", "humility",
    "bravery", "selflessness", "responsibility", "determination",
    "sight", "sound", "smell", "taste", "touch",
    "vision", "hearing", "aroma", "flavor", "texture",
    "pain", "pleasure", "warmth", "cold", "light",
    "dark", "soul", "spirit", "god", "goddess",
    "angel", "demon", "heaven", "hell", "karma",
    "reincarnation", "meditation", "prayer", "shrine", "temple",
    "church", "mosque", "synagogue", "truth", "beauty",
    "good", "evil", "justice", "freedom", "equality",
    "virtue", "vice", "logic", "reason", "ethics",
    "morality", "aesthetics", "ontology", "epistemology",
    "time", "space", "moment", "hour", "day",
    "week", "month", "year", "decade", "century",
    "millennium", "past", "present", "future", "distance",
    "height", "width", "depth", "length", "area",
    "volume", "red", "blue", "green", "yellow",
    "black", "white", "purple", "pink", "orange",
    "brown", "gray", "silver", "gold", "bronze",
    "turquoise", "violet", "heart", "cross", "star of David",
    "crescent moon", "yin - yang", "peace sign", "dove", "olive branch",
    "rose", "lotus", "anchor", "ladder", "idea",
    "thought", "concept", "theory", "knowledge", "information",
    "power", "energy", "art", "culture", "history",
    "memory", "dream", "fantasy", "reality", "illusion"
]

# 定义文件图标类名和颜色的函数
def get_file_icon_class(file):
    ext = file.split('.')[-1].lower()
    icon_classes = {
        'pdf': 'fa-solid fa-file-pdf',
        'docx': 'fa-solid fa-file-word',
        'xlsx': 'fa-solid fa-file-excel',
        'pptx': 'fa-solid fa-file-powerpoint'
    }
    return icon_classes.get(ext, 'fa-solid fa-file')

def get_file_icon_color(file):
    ext = file.split('.')[-1].lower()
    icon_colors = {
        'pdf': '#e74c3c',
        'docx': '#2ecc71',
        'xlsx': '#f1c40f',
        'pptx': '#3498db'
    }
    return icon_colors.get(ext, '#95a5a6')

# 将函数注册为 Jinja2 全局函数
app.jinja_env.globals.update(get_file_icon_class=get_file_icon_class)
app.jinja_env.globals.update(get_file_icon_color=get_file_icon_color)

def generate_random_string(length):
    """生成指定长度的不可读随机字符串"""
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))

def generate_keys():
    now = datetime.now()
    seed = f"{now.year}{now.month}{now.day}{now.hour}{now.minute}{now.second}"
    random.seed(seed)
    correct_key = random.choice(MEANINGFUL_WORDS)
    wrong_keys = [generate_random_string(random.randint(5, 9)) for _ in range(9)]
    all_keys = [correct_key] + wrong_keys
    random.shuffle(all_keys)
    return all_keys, correct_key

def calculate_file_hash(file):
    """计算文件的哈希值"""
    hash_object = hashlib.sha256()
    for chunk in iter(lambda: file.read(4096), b""):
        hash_object.update(chunk)
    file.seek(0)  # 将文件指针重置到文件开头
    return hash_object.hexdigest()

def check_file_hash_exists(file_hash):
    """检查哈希值是否已存在"""
    with open(HASH_FILE, 'r') as f:
        hashes = f.read().splitlines()
    return file_hash in hashes

def add_file_hash(file_hash):
    """将哈希值添加到文件中"""
    with open(HASH_FILE, 'a') as f:
        f.write(file_hash + '\n')

@app.route('/', methods=['GET', 'POST'])
def index():
    # 获取上传文件夹中的所有文件列表并复制到剪贴板
    uploaded_files = os.listdir(app.config['UPLOAD_FOLDER'])
    formatted_files = [f"'{file}'" for file in uploaded_files]
    files_list_str = f"[{', '.join(formatted_files)}]"
    print("Uploaded Files:", files_list_str)
    pyperclip.copy("const pdfFiles =" + files_list_str + ";")

    error = ''
    uploaded_files = os.listdir(app.config['UPLOAD_FOLDER'])
    keys, correct_key = generate_keys()

    if request.method == 'POST':
        file = request.files['file']
        selected_key = request.form.get('selectedKey')
        if selected_key != "None":
            if selected_key not in MEANINGFUL_WORDS:
                error = 'None'
            elif file:
                # 计算文件的哈希值
                file_hash = calculate_file_hash(file.stream)
                if check_file_hash_exists(file_hash):
                    print(f"文件 {file.filename} 已存在。")
                    error = "None"
                else:
                    # 获取原始文件名
                    original_filename = file.filename
                    # 去掉 _freemagazines_top 及其后面的内容
                    if '_freemagazines_top' in original_filename:
                        new_filename = original_filename.split('_freemagazines_top')[0]
                        if not new_filename.endswith('.pdf'):
                            new_filename += '.pdf'
                    else:
                        new_filename = original_filename
                    # 将文件名中的 _ 替换为空格
                    new_filename = new_filename.replace('_', ' ')
                    # 确保文件名是唯一的，避免覆盖
                    base_name, ext = os.path.splitext(new_filename)
                    counter = 1
                    while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], new_filename)):
                        new_filename = f"{base_name} ({counter}){ext}"
                        counter += 1
                    # 保存文件到指定目录
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))
                    # 将哈希值添加到文件中
                    add_file_hash(file_hash)
                    selected_key = "None"
                    return redirect(url_for('index'))

    return render_template('index.html', error=error, uploaded_files=uploaded_files, keys=keys)

if __name__ == '__main__':
    app.run(debug=True)