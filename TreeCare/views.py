import csv
from itertools import groupby
import random
from django.http import HttpResponse
from django.shortcuts import redirect, render
import joblib
import numpy as np
from sklearn.decomposition import PCA
from .models import *
from joblib import dump, load
from sklearn.preprocessing import StandardScaler
from django.db import transaction

def index(request):
    return render(request, 'main.html')

def predict_and_update_tree_status():
    # Lấy tất cả cây trồng
    trees = Tree.objects.all()

    # Chuẩn bị dữ liệu đầu vào cho mô hình
    features = []
    ids = []
    
    # Lấy các đặc trưng của mỗi cây trồng
    for tree in trees:
        features.append([
            tree.SoilMoisture,
            tree.Temperature,
            tree.SoilHumidity,
            tree.Time,
            tree.AirTemperature,
            tree.WindSpeed,
            tree.Airhumidity,
            tree.Windgust,
            tree.Pressure,
            tree.ph,
            tree.rainfall,
            tree.N,
            tree.P,
            tree.K
        ])
        ids.append(tree.id)  # Lưu lại ID của cây để dễ dàng cập nhật sau này

    # Chuyển đổi features thành numpy array
    X = np.array(features)

    # Chuẩn hóa các đặc trưng
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Tải mô hình đã huấn luyện
    model_loaded = load('decision_tree_model.joblib')

    # Dự đoán trạng thái cho tất cả cây trồng
    predictions = model_loaded.predict(X_scaled)

    # Cập nhật trạng thái của mỗi cây trong cơ sở dữ liệu
    for i, tree in enumerate(trees):
        # Mã hóa lại trạng thái (1 là ON, 0 là OFF)
        if predictions[i] == 1:
            tree.Status = "ON"
        else:
            tree.Status = "OFF"
        tree.save()  # Lưu lại thay đổi trong cơ sở dữ liệu

def update_random_values():
    # Lấy tất cả cây trồng
    trees = Tree.objects.all()

    # Duyệt qua từng cây trồng để cập nhật giá trị ngẫu nhiên cho N, P, K, và AirTemperature
    trees_to_update = []
    for tree in trees:
        # Tạo giá trị ngẫu nhiên cho N, P, K
        tree.N = random.randint(0, 140)  # N trong khoảng từ 0 đến 140
        tree.P = random.randint(5, 145)  # P trong khoảng từ 5 đến 145
        tree.K = random.randint(5, 205)  # K trong khoảng từ 5 đến 205
        
        # Tạo giá trị ngẫu nhiên cho AirTemperature trong khoảng từ 12 đến 40 độ và làm tròn đến 2 chữ số
        tree.AirTemperature = round(random.uniform(12, 40), 2)

        trees_to_update.append(tree)

    # Cập nhật tất cả các cây trong một giao dịch duy nhất
    with transaction.atomic():
        Tree.objects.bulk_update(trees_to_update, ['N', 'P', 'K', 'AirTemperature'])

    print("Cập nhật giá trị ngẫu nhiên cho N, P, K, và AirTemperature thành công!")
def home(request):
    trees = Tree.objects.all()
    # Nhóm cây trồng theo cluster
    grouped_trees = {}
    for cluster, group in groupby(trees, key=lambda x: x.Cluster):
        grouped_trees[cluster] = list(group)
    print(len(list(grouped_trees)))
    context = {
        'grouped_trees': grouped_trees
    }
    # Gọi hàm cập nhật giá trị ngẫu nhiên cho N, P, K
    update_random_values()

    # Gọi hàm dự đoán và cập nhật trạng thái cho cây
    predict_and_update_tree_status()

    return render(request, 'home.html', context)



from django.shortcuts import render
from .models import Tree
import pandas as pd

def add_tree(request):
    if request.method == 'POST':
        # Lấy dữ liệu từ form
        soil_moisture = float(request.POST.get('SoilMoisture'))
        temperature = float(request.POST.get('Temperature'))
        soil_humidity = float(request.POST.get('SoilHumidity'))
        time = float(request.POST.get('Time'))
        air_temperature = float(request.POST.get('AirTemperature'))
        wind_speed = float(request.POST.get('WindSpeed'))
        air_humidity = float(request.POST.get('Airhumidity'))
        windgust = float(request.POST.get('Windgust'))
        pressure = float(request.POST.get('Pressure'))
        ph = float(request.POST.get('ph'))
        rainfall = float(request.POST.get('rainfall'))
        N = float(request.POST.get('N'))
        P = float(request.POST.get('P'))
        K = float(request.POST.get('K'))
        status = request.POST.get('Status')


        # Dữ liệu đầu vào cho mô hình
        X_input = [[soil_moisture, temperature, soil_humidity, time, air_temperature, wind_speed,
                    air_humidity, windgust, pressure, ph, rainfall, N, P, K]]
        
        # Tải mô hình KMeans đã lưu
        model_loaded = joblib.load('decision_tree_cluster_model.joblib')

        # Tải scaler và PCA đã được khớp từ tập huấn luyện
        scaler = StandardScaler()  # Đảm bảo scaler được lưu trước đó
        X_scaled = scaler.fit_transform(X_input)


        # Dự đoán trạng thái cho tất cả cây trồng
        predictions = model_loaded.predict(X_scaled)
        

        cluster_name = predictions[0]

        # Tạo đối tượng Tree mới và lưu vào database
        new_tree = Tree(
            SoilMoisture=soil_moisture,
            Temperature=temperature,
            SoilHumidity=soil_humidity,
            Time=time,
            AirTemperature=air_temperature,
            WindSpeed=wind_speed,
            Airhumidity=air_humidity,
            Windgust=windgust,
            Pressure=pressure,
            ph=ph,
            rainfall=rainfall,
            N=N,
            P=P,
            K=K,
            Status=status,
            Cluster=cluster_name  # Gán giá trị cụm đã dự đoán
        )
        new_tree.save()

        # Chuyển hướng tới trang index hoặc hiển thị thông báo thành công
        return redirect('index')

    # Hiển thị form thêm cây
    return render(request, 'add_tree.html')

# ------------------------------------------------Import CSV----------------------------------------------
import pandas as pd
def create_db_tree(file_path):
    df = pd.read_csv(file_path, delimiter=',')
    list_of_csv = [list(row) for row in df.values]

    for l in list_of_csv:
        Tree.objects.create(
            SoilMoisture=l[0],
            Temperature=l[1],
            SoilHumidity=l[2],
            Time=l[3],
            AirTemperature=l[4],
            WindSpeed=l[5],
            Airhumidity=l[6],
            Windgust=l[7],
            Pressure=l[8],
            ph=l[9],
            rainfall=l[10],
            N=l[11],
            P=l[12],
            K=l[13],
            Status=l[14],
            Cluster=l[15]
        )
def import_csv(request):
    if request.method == 'POST':
        file = request.FILES['file']
        obj = File.objects.create(file=file)
        create_db_tree(obj.file)

        return redirect('index')

    return render(request, 'import.html')

# ------------------------------------------------Export CSV----------------------------------------------
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="customer.csv"'

    writer = csv.writer(response)
    writer.writerow(['SoilMoisture', 'Temperature', 'SoilHumidity', 'Time', 'AirTemperature', 'WindSpeed', 'Airhumidity', 'Windgust', 'Pressure', 'ph', 'rainfall', 'N', 'P', 'K', 'Status', 'Cluster'])

    Treees = Tree.objects.all().values_list('SoilMoisture', 'Temperature', 'SoilHumidity', 'Time', 'AirTemperature', 'WindSpeed', 'Airhumidity', 'Windgust', 'Pressure', 'ph', 'rainfall', 'N', 'P', 'K', 'Status', 'Cluster')
    for Treee in Treees:
        writer.writerow(Treee)

    return response