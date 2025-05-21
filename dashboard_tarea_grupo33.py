import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import warnings
warnings.filterwarnings("ignore")

# Cargar datos
file_id = "1Dy_75hdwKS1fG4YtEtfB-Dp3SBLXa9H0"
url= f"https://drive.google.com/uc?export=download&id={file_id}"
df = pd.read_csv(url)

# Procesar fechas
df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')
df['Date_fmt'] = df['Date'].dt.strftime('%d/%m/%Y')

st.title("Análisis Interactivo de Ventas")

# --- FILTROS ---

# Filtro rango fechas
min_date = df['Date'].min()
max_date = df['Date'].max()
date_range = st.sidebar.date_input("Seleccione rango de fechas", [min_date, max_date], min_value=min_date, max_value=max_date)

if len(date_range) == 2:
    start_date, end_date = date_range
    df = df[(df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))]

# Filtro línea de producto
product_lines = df['Product line'].unique()
selected_lines = st.sidebar.multiselect("Seleccionar líneas de producto", product_lines, default=product_lines)
df = df[df['Product line'].isin(selected_lines)]

# Filtro tipo cliente
customer_types = df['Customer type'].unique()
selected_customers = st.sidebar.multiselect("Seleccionar tipo de cliente", customer_types, default=customer_types)
df = df[df['Customer type'].isin(selected_customers)]

# Filtro rango rating
min_rating = float(df['Rating'].min())
max_rating = float(df['Rating'].max())
rating_range = st.sidebar.slider("Rango de calificación (Rating)", min_rating, max_rating, (min_rating, max_rating))
df = df[(df['Rating'] >= rating_range[0]) & (df['Rating'] <= rating_range[1])]

st.write(f"Datos filtrados: {df.shape[0]} filas")

# --- GRÁFICOS ---

# 1. Evolución ventas totales
st.subheader("1. Evolución de las Ventas Totales")

sales_over_time = df.groupby('Date')['Total'].sum().reset_index()
sales_over_time['Rolling Mean'] = sales_over_time['Total'].rolling(window=7, min_periods=1).mean()

max_row = sales_over_time.loc[sales_over_time['Total'].idxmax()]
min_row = sales_over_time.loc[sales_over_time['Total'].idxmin()]

fig, ax = plt.subplots(figsize=(14, 6))
sns.lineplot(data=sales_over_time, x='Date', y='Total', label='Ventas Diarias', color='teal', marker='o', ax=ax)
sns.lineplot(data=sales_over_time, x='Date', y='Rolling Mean', label='Tendencia (media móvil 7 días)', color='orange', linestyle='--', ax=ax)

ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d/%m/%Y'))
plt.xticks(rotation=45)

ax.annotate(f'Máximo: {max_row.Total:,.0f}',
            xy=(max_row.Date, max_row.Total),
            xytext=(max_row.Date, max_row.Total + 150),
            arrowprops=dict(facecolor='green', arrowstyle='->'),
            fontsize=10, backgroundcolor='white')

ax.annotate(f'Mínimo: {min_row.Total:,.0f}',
            xy=(min_row.Date, min_row.Total),
            xytext=(min_row.Date, min_row.Total - 200),
            arrowprops=dict(facecolor='red', arrowstyle='->'),
            fontsize=10, backgroundcolor='white')

ax.set_title('Evolución de las Ventas Totales a lo Largo del Tiempo', fontsize=16, fontweight='bold')
ax.set_xlabel('Fecha', fontsize=12)
ax.set_ylabel('Ventas Totales', fontsize=12)
ax.grid(True, linestyle='--', alpha=0.5)
ax.legend()
st.pyplot(fig)

# 2. Ingresos por Línea de Producto
st.subheader("2. Ingresos por Línea de Producto")

order = df.groupby('Product line')['Total'].sum().sort_values(ascending=True).index
grouped = df.groupby('Product line')['Total'].sum().reindex(order)

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(data=df, x='Product line', y='Total', estimator=sum, palette='viridis', order=order, ax=ax)

for index, value in enumerate(grouped):
    ax.text(index, value + 20, f'{value:,.0f}', ha='center', va='bottom', fontsize=9)

ax.set_title('Ingresos Totales por Línea de Producto', fontsize=16, fontweight='bold')
ax.set_xlabel('Línea de Producto', fontsize=12)
ax.set_ylabel('Ingresos Totales', fontsize=12)
plt.xticks(rotation=45)
st.pyplot(fig)

# 3. Distribución de Calificación de Clientes
st.subheader("3. Distribución de la Calificación de Clientes")

mean_rating = df['Rating'].mean()
median_rating = df['Rating'].median()

fig, ax = plt.subplots(figsize=(10, 6))
sns.histplot(df['Rating'], bins=10, kde=True, color='skyblue', edgecolor='gray', label='Histograma', ax=ax)
sns.rugplot(df['Rating'], height=0.05, color='darkblue', label='Puntos de datos (rugplot)', ax=ax)
ax.axvline(mean_rating, color='red', linestyle='--', linewidth=2, label=f'Media: {mean_rating:.2f}')
ax.axvline(median_rating, color='green', linestyle=':', linewidth=2, label=f'Mediana: {median_rating:.2f}')
ax.set_title('Distribución de la Calificación de Clientes', fontsize=16, fontweight='bold')
ax.set_xlabel('Rating', fontsize=12)
ax.set_ylabel('Frecuencia', fontsize=12)
ax.legend(title='Elementos del gráfico', loc='center left', bbox_to_anchor=(1, 0.5))
plt.tight_layout()
st.pyplot(fig)

# 4. Comparación del Gasto por Tipo de Cliente
st.subheader("4. Comparación del Gasto por Tipo de Cliente")

fig, ax = plt.subplots(figsize=(10, 6))
palette = sns.color_palette("pastel")
sns.boxplot(data=df, x='Customer type', y='Total', palette=palette, ax=ax)
sns.pointplot(data=df, x='Customer type', y='Total', estimator='mean', color='black', join=False, markers='D', ax=ax)

ax.set_title('Distribución del Gasto por Tipo de Cliente', fontsize=16, fontweight='bold')
ax.set_xlabel('Tipo de Cliente', fontsize=12)
ax.set_ylabel('Total Gastado', fontsize=12)

fig.text(1.02, 0.5,
         '🔹 Cada caja representa el gasto total\n'
         '   para cada tipo de cliente.\n\n'
         '🔹 La línea horizontal dentro de la caja\n'
         '   es la **mediana** del gasto.\n\n'
         '🔹 Los puntos aislados son valores **atípicos**\n'
         '   (clientes con gastos extremos).\n\n'
         '🔹 Los diamantes negros representan la **media**.',
         fontsize=10, va='center', ha='left', color='dimgray')

plt.tight_layout(rect=[0, 0, 0.9, 1])
st.pyplot(fig)

# 5. Relación entre Costo y Ganancia Bruta
st.subheader("5. Relación entre Costo y Ganancia Bruta")

fig, ax = plt.subplots(figsize=(10, 6))
sns.scatterplot(
    data=df,
    x='cogs',
    y='gross income',
    hue='Branch',
    palette='Dark2',
    alpha=0.6,
    s=40,
    edgecolor='w',
    linewidth=0.5,
    ax=ax
)

ax.set_title('Relación entre Costo y Ganancia Bruta', fontsize=16, fontweight='bold')
ax.set_xlabel('Costo de Bienes Vendidos (COGS)', fontsize=12)
ax.set_ylabel('Ingreso Bruto (Gross Income)', fontsize=12)

fig.text(1.02, 0.5,
         '🔹 Cada punto representa una transacción.\n\n'
         '🔹 El eje X muestra el costo del producto (cogs).\n\n'
         '🔹 El eje Y muestra la ganancia generada (gross income).\n\n'
         '🔹 Los colores indican la sucursal.\n\n'
         '🔹 Existe una relación lineal positiva:\n'
         '   mayor costo tiende a generar mayor ganancia.',
         fontsize=10, va='center', ha='left', color='dimgray')

plt.tight_layout(rect=[0, 0, 0.9, 1])
st.pyplot(fig)

# 6. Sucursales y Métodos de Pago
st.subheader("6. Ventas por Sucursal y Método de Pago")

branch_payment = df.groupby(['Branch', 'Payment'])['Total'].sum().unstack().fillna(0)

fig, ax = plt.subplots(figsize=(12, 6))
branch_payment.plot(kind='bar', stacked=True, ax=ax, colormap='Set3')

ax.set_title('Ventas Totales por Sucursal y Método de Pago', fontsize=16, fontweight='bold')
ax.set_xlabel('Sucursal', fontsize=12)
ax.set_ylabel('Total Ventas', fontsize=12)
ax.legend(title='Método de Pago', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.xticks(rotation=0)
plt.tight_layout()
st.pyplot(fig)
