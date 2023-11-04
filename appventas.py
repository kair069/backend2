from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import mysql.connector
import pandas as pd
import xlsxwriter
import io
import openpyxl

app = Flask(__name__)
CORS(app, origins="*")

# Configura la conexión a MySQL
db = mysql.connector.connect(
    host="mysqlalex.mysql.database.azure.com",
    user="administrador",
    password="boltimax.P",
    database="mi_base_de_datos"
)

# Modifica la tabla para incluir 6 variables en "productosa"
# Asumiremos que tenemos campos como nombre, descripción, precio, cantidad en stock, proveedor y categoría.

@app.route('/productos', methods=['GET'])
def listar_productos():
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM productosa")
        productos = cursor.fetchall()
        return jsonify(productos)
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route('/productos', methods=['POST'])
def agregar_producto():
    try:
        data = request.get_json()
        nombre = data['nombre']
        descripcion = data['descripcion']
        precio = data['precio']
        cantidad_stock = data['cantidad_stock']
        proveedor = data['proveedor']
        categoria = data['categoria']

        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO productosa (nombre, descripcion, precio, cantidad_stock, proveedor, categoria) VALUES (%s, %s, %s, %s, %s, %s)",
            (nombre, descripcion, precio, cantidad_stock, proveedor, categoria)
        )
        db.commit()
        return jsonify({"mensaje": "Producto agregado correctamente"})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/productos/<int:producto_id>', methods=['GET', 'PUT', 'DELETE'])
def gestionar_producto(producto_id):
    try:
        cursor = db.cursor(dictionary=True)
        if request.method == 'GET':
            cursor.execute("SELECT * FROM productosa WHERE id = %s", (producto_id,))
            producto = cursor.fetchone()
            if producto:
                return jsonify(producto)
            else:
                return jsonify({"mensaje": "Producto no encontrado"}), 404
        elif request.method == 'PUT':
            data = request.get_json()
            nombre = data['nombre']
            descripcion = data['descripcion']
            precio = data['precio']
            cantidad_stock = data['cantidad_stock']
            proveedor = data['proveedor']
            categoria = data['categoria']

            cursor.execute(
                "UPDATE productosa SET nombre = %s, descripcion = %s, precio = %s, cantidad_stock = %s, proveedor = %s, categoria = %s WHERE id = %s",
                (nombre, descripcion, precio, cantidad_stock, proveedor, categoria, producto_id)
            )
            db.commit()
            return jsonify({"mensaje": "Producto actualizado correctamente"})
        elif request.method == 'DELETE':
            cursor.execute("DELETE FROM productosa WHERE id = %s", (producto_id,))
            db.commit()
            return jsonify({"mensaje": "Producto eliminado correctamente"})
    except Exception as e:
        return jsonify({"error": str(e)})

# Rutas para exportar datos a CSV y Excel

@app.route('/productos/export-csv', methods=['GET'])
def export_to_csv():
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM productosa")
        productos = cursor.fetchall()

        # Convert the product data to a DataFrame
        df = pd.DataFrame(productos)

        # Create an in-memory CSV writer object
        output = io.StringIO()

        # Write the DataFrame to the StringIO object in binary mode
        df.to_csv(output, index=False, encoding='utf-8', mode='w', header=True, sep=',', quotechar='"')

        # Save the CSV data to the output stream
        output.seek(0)

        # Return the CSV file as a downloadable attachment
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            as_attachment=True,
            download_name='productos.csv',
            mimetype='text/csv'
        )

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/productos/export-excel', methods=['GET'])
def export_to_excel():
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM productosa")
        productos = cursor.fetchall()

        # Convert the product data to a DataFrame
        df = pd.DataFrame(productos)

        # Create an in-memory Excel writer object
        output = io.BytesIO()

        # Create a Pandas Excel writer using openpyxl as the engine
        writer = pd.ExcelWriter(output, engine='openpyxl')

        # Write the DataFrame to the Excel writer
        df.to_excel(writer, sheet_name='productos', index=False)

        # Save the Excel workbook to the output stream
        writer.save()
        output.seek(0)

        # Return the Excel file as a downloadable attachment
        return send_file(
            io.BytesIO(output.read()),
            as_attachment=True,
            download_name='productos.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
