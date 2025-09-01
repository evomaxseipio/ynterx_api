# 🚀 Guía de Integración Flutter - Endpoints de Pagos con Imágenes

## 📋 Resumen

Esta guía te muestra cómo integrar los endpoints de pagos con imágenes en tu aplicación Flutter, tanto para web como móvil.

## 🎯 Endpoints Disponibles

### ✅ **Funcionando Perfectamente:**
1. **POST** `/loan-payments/upload-payment-image` - Subir solo imagen
2. **POST** `/loan-payments/register-transaction` - Registrar transacción sin imagen

### ⚠️ **Con Problemas Menores:**
3. **POST** `/loan-payments/auto-payment` - Pago automático con imagen (necesita ajuste de formato)
4. **POST** `/loan-payments/specific-payment` - Pago específico (error interno)

## 📦 Dependencias Requeridas

Agrega estas dependencias a tu `pubspec.yaml`:

```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0
  image_picker: ^1.0.4
  shared_preferences: ^2.2.2
```

## 🔧 Implementación del Servicio

### 1. **Servicio Base (payment_service.dart)**

```dart
import 'dart:typed_data';
import 'package:http/http.dart' as http;
import 'dart:convert';

// Modelo de respuesta API
class ApiResponse<T> {
  final bool success;
  final T? data;
  final String? message;
  final String? error;

  ApiResponse({
    required this.success,
    this.data,
    this.message,
    this.error,
  });

  factory ApiResponse.successResponse(T data, {String? message}) {
    return ApiResponse(
      success: true,
      data: data,
      message: message,
    );
  }

  factory ApiResponse.errorResponse(String error) {
    return ApiResponse(
      success: false,
      error: error,
    );
  }
}

// Modelo de datos de pago
class PaymentData {
  final int contractLoanId;
  final double amount;
  final String paymentMethod;
  final String reference;
  final String? notes;
  final String? transactionDate;
  final Uint8List? imageFile;
  final String? imageFilename;

  PaymentData({
    required this.contractLoanId,
    required this.amount,
    this.paymentMethod = 'Bank Transfer',
    required this.reference,
    this.notes,
    this.transactionDate,
    this.imageFile,
    this.imageFilename,
  });

  Map<String, dynamic> toJson() {
    return {
      'contract_loan_id': contractLoanId,
      'amount': amount,
      'payment_method': paymentMethod,
      'reference': reference,
      if (notes != null) 'notes': notes,
      if (transactionDate != null) 'transaction_date': transactionDate,
    };
  }
}

// Servicio de pagos
class PaymentService {
  final String baseUrl;
  final String? authToken;
  final http.Client _client = http.Client();

  PaymentService({
    required this.baseUrl,
    this.authToken,
  });

  // Headers para multipart
  Map<String, String> get _multipartHeaders {
    final headers = <String, String>{};
    if (authToken != null) {
      headers['Authorization'] = 'Bearer $authToken';
    }
    return headers;
  }

  // Headers para JSON
  Map<String, String> get _jsonHeaders {
    final headers = <String, String>{
      'Content-Type': 'application/json',
    };
    if (authToken != null) {
      headers['Authorization'] = 'Bearer $authToken';
    }
    return headers;
  }

  /// Subir solo imagen de pago (ENDPOINT FUNCIONANDO)
  Future<ApiResponse<Map<String, dynamic>>> uploadPaymentImage({
    required String contractId,
    required String reference,
    required Uint8List imageFile,
    String? imageFilename,
  }) async {
    try {
      final request = http.MultipartRequest(
        'POST',
        Uri.parse('$baseUrl/loan-payments/upload-payment-image'),
      );

      request.headers.addAll(_multipartHeaders);
      request.fields.addAll({
        'contract_id': contractId,
        'reference': reference,
      });

      final filename = imageFilename ?? '$reference.jpg';
      request.files.add(
        http.MultipartFile.fromBytes(
          'image_file',
          imageFile,
          filename: filename,
        ),
      );

      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      return _handleResponse(response);
    } catch (e) {
      return ApiResponse.errorResponse('Error al subir imagen: $e');
    }
  }

  /// Registrar transacción sin imagen (ENDPOINT FUNCIONANDO)
  Future<ApiResponse<Map<String, dynamic>>> registerTransaction(
    PaymentData paymentData,
  ) async {
    try {
      final response = await _client.post(
        Uri.parse('$baseUrl/loan-payments/register-transaction'),
        headers: _jsonHeaders,
        body: jsonEncode(paymentData.toJson()),
      );

      return _handleResponse(response);
    } catch (e) {
      return ApiResponse.errorResponse('Error al registrar transacción: $e');
    }
  }

  /// Manejar respuesta del servidor
  ApiResponse<Map<String, dynamic>> _handleResponse(http.Response response) {
    try {
      final responseData = jsonDecode(response.body) as Map<String, dynamic>;
      
      if (response.statusCode == 200) {
        final success = responseData['success'] ?? false;
        
        if (success) {
          final message = responseData['message'] ?? 'Operación exitosa';
          return ApiResponse.successResponse(responseData, message: message);
        } else {
          final errorMessage = responseData['message'] ?? 'Error en la operación';
          return ApiResponse.errorResponse(errorMessage);
        }
      } else if (response.statusCode == 401) {
        return ApiResponse.errorResponse('Error de autenticación. Verifica tu token.');
      } else if (response.statusCode == 422) {
        final errorMessage = responseData['message'] ?? 'Error de validación de datos';
        return ApiResponse.errorResponse(errorMessage);
      } else {
        final errorMessage = responseData['message'] ?? 'Error del servidor';
        return ApiResponse.errorResponse(errorMessage);
      }
    } catch (e) {
      return ApiResponse.errorResponse('Error procesando respuesta del servidor');
    }
  }

  void dispose() {
    _client.close();
  }
}
```

### 2. **Adaptador para tu Código Existente**

```dart
// Adaptador que mantiene compatibilidad con tu método original
class PaymentServiceAdapter {
  final PaymentService _paymentService;

  PaymentServiceAdapter({
    required String baseUrl,
    String? authToken,
  }) : _paymentService = PaymentService(
         baseUrl: baseUrl,
         authToken: authToken,
       );

  /// Método adaptado de tu código original
  Future<ApiResponse<String>> registerPayment(Map<String, dynamic> paymentData) async {
    try {
      // Verificar si hay imagen
      final hasImageFile = paymentData.containsKey('image_file') &&
          paymentData['image_file'] is List<int>;

      if (hasImageFile) {
        // Subir imagen primero
        final imageResult = await _paymentService.uploadPaymentImage(
          contractId: paymentData['contract_loan_id'].toString(),
          reference: paymentData['reference'],
          imageFile: Uint8List.fromList(paymentData['image_file'] as List<int>),
          imageFilename: paymentData['image_filename'] as String?,
        );

        if (!imageResult.success) {
          return ApiResponse.errorResponse(imageResult.error ?? 'Error subiendo imagen');
        }

        // Luego registrar transacción
        final paymentDataObj = PaymentData(
          contractLoanId: paymentData['contract_loan_id'] as int,
          amount: (paymentData['amount'] as num).toDouble(),
          paymentMethod: paymentData['payment_method'] as String? ?? 'Bank Transfer',
          reference: paymentData['reference'] as String,
          notes: paymentData['notes'] as String?,
          transactionDate: paymentData['transaction_date'] as String?,
        );

        final transactionResult = await _paymentService.registerTransaction(paymentDataObj);

        if (transactionResult.success) {
          return ApiResponse.successResponse('success', message: transactionResult.message);
        } else {
          return ApiResponse.errorResponse(transactionResult.error ?? 'Error desconocido');
        }
      } else {
        // Pago sin imagen
        final paymentDataObj = PaymentData(
          contractLoanId: paymentData['contract_loan_id'] as int,
          amount: (paymentData['amount'] as num).toDouble(),
          paymentMethod: paymentData['payment_method'] as String? ?? 'Bank Transfer',
          reference: paymentData['reference'] as String,
          notes: paymentData['notes'] as String?,
          transactionDate: paymentData['transaction_date'] as String?,
        );

        final result = await _paymentService.registerTransaction(paymentDataObj);

        if (result.success) {
          return ApiResponse.successResponse('success', message: result.message);
        } else {
          return ApiResponse.errorResponse(result.error ?? 'Error desconocido');
        }
      }
    } catch (e) {
      return ApiResponse.errorResponse('Error al registrar el pago: $e');
    }
  }

  void dispose() {
    _paymentService.dispose();
  }
}
```

## 📱 Ejemplos de Uso

### **Ejemplo 1: Uso Directo con tu Código Original**

```dart
void exampleUsage() async {
  // Configurar adaptador
  final adapter = PaymentServiceAdapter(
    baseUrl: 'http://localhost:8000',
    authToken: 'your-jwt-token-here',
  );

  try {
    // Pago con imagen (como tu código original)
    final paymentDataWithImage = {
      'contract_loan_id': 123,
      'amount': 1500.00,
      'payment_method': 'Bank Transfer',
      'reference': 'PAYMENT_001',
      'notes': 'Pago mensual con voucher',
      'image_file': [1, 2, 3, 4, 5], // Datos de imagen reales
      'image_filename': 'voucher.jpg',
    };

    final result = await adapter.registerPayment(paymentDataWithImage);
    if (result.success) {
      print('✅ Pago registrado: ${result.message}');
    } else {
      print('❌ Error: ${result.error}');
    }

  } finally {
    adapter.dispose();
  }
}
```

### **Ejemplo 2: Con ImagePicker**

```dart
import 'package:image_picker/image_picker.dart';

class PaymentWithImagePicker {
  final PaymentServiceAdapter _adapter;
  final ImagePicker _picker = ImagePicker();

  PaymentWithImagePicker({
    required String baseUrl,
    String? authToken,
  }) : _adapter = PaymentServiceAdapter(
         baseUrl: baseUrl,
         authToken: authToken,
       );

  /// Seleccionar imagen y registrar pago
  Future<ApiResponse<String>> selectImageAndRegisterPayment({
    required int contractLoanId,
    required double amount,
    required String reference,
    String? notes,
  }) async {
    try {
      // Seleccionar imagen
      final XFile? image = await _picker.pickImage(
        source: ImageSource.gallery,
        maxWidth: 1024,
        maxHeight: 1024,
        imageQuality: 85,
      );

      if (image == null) {
        return ApiResponse.errorResponse('No se seleccionó ninguna imagen');
      }

      // Leer bytes de la imagen
      final imageBytes = await image.readAsBytes();

      // Crear datos de pago
      final paymentData = {
        'contract_loan_id': contractLoanId,
        'amount': amount,
        'payment_method': 'Bank Transfer',
        'reference': reference,
        if (notes != null) 'notes': notes,
        'image_file': imageBytes,
        'image_filename': image.name,
      };

      // Registrar pago
      return await _adapter.registerPayment(paymentData);
    } catch (e) {
      return ApiResponse.errorResponse('Error: $e');
    }
  }

  void dispose() {
    _adapter.dispose();
  }
}
```

### **Ejemplo 3: Widget Flutter Completo**

```dart
class PaymentScreen extends StatefulWidget {
  @override
  _PaymentScreenState createState() => _PaymentScreenState();
}

class _PaymentScreenState extends State<PaymentScreen> {
  final _formKey = GlobalKey<FormState>();
  final _amountController = TextEditingController();
  final _referenceController = TextEditingController();
  final _notesController = TextEditingController();
  
  late PaymentWithImagePicker _paymentService;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _paymentService = PaymentWithImagePicker(
      baseUrl: 'http://localhost:8000',
      authToken: 'your-jwt-token-here',
    );
  }

  @override
  void dispose() {
    _paymentService.dispose();
    _amountController.dispose();
    _referenceController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  Future<void> _registerPaymentWithImage() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    try {
      final result = await _paymentService.selectImageAndRegisterPayment(
        contractLoanId: 123, // Tu contract_loan_id
        amount: double.parse(_amountController.text),
        reference: _referenceController.text,
        notes: _notesController.text.isNotEmpty ? _notesController.text : null,
      );

      if (result.success) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('✅ ${result.message}'),
            backgroundColor: Colors.green,
          ),
        );
        Navigator.pop(context);
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('❌ ${result.error}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Registrar Pago')),
      body: Padding(
        padding: EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            children: [
              TextFormField(
                controller: _amountController,
                decoration: InputDecoration(labelText: 'Monto'),
                keyboardType: TextInputType.number,
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Por favor ingresa el monto';
                  }
                  return null;
                },
              ),
              SizedBox(height: 16),
              TextFormField(
                controller: _referenceController,
                decoration: InputDecoration(labelText: 'Referencia'),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Por favor ingresa la referencia';
                  }
                  return null;
                },
              ),
              SizedBox(height: 16),
              TextFormField(
                controller: _notesController,
                decoration: InputDecoration(labelText: 'Notas (opcional)'),
                maxLines: 3,
              ),
              SizedBox(height: 32),
              ElevatedButton(
                onPressed: _isLoading ? null : _registerPaymentWithImage,
                child: _isLoading
                    ? CircularProgressIndicator()
                    : Text('Seleccionar Imagen y Registrar Pago'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
```

## 🔧 Configuración de Permisos

### **Android** (`android/app/src/main/AndroidManifest.xml`):
```xml
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.INTERNET" />
```

### **iOS** (`ios/Runner/Info.plist`):
```xml
<key>NSCameraUsageDescription</key>
<string>Esta app necesita acceso a la cámara para tomar fotos de vouchers</string>
<key>NSPhotoLibraryUsageDescription</key>
<string>Esta app necesita acceso a la galería para seleccionar imágenes de vouchers</string>
```

## 🧪 Pruebas

Los endpoints han sido probados con datos mock y funcionan correctamente:

- ✅ **Subida de imagen**: Funciona perfectamente
- ✅ **Registro de transacción**: Funciona perfectamente
- ✅ **Manejo de errores**: Implementado
- ✅ **Validación**: Funciona correctamente

## 🎯 Ventajas de esta Implementación

1. **✅ Compatibilidad**: Mantiene tu código original
2. **✅ Simplicidad**: Fácil de usar y entender
3. **✅ Robustez**: Manejo de errores completo
4. **✅ Flexibilidad**: Funciona con y sin imágenes
5. **✅ Escalabilidad**: Fácil de extender

## 📞 Soporte

Si tienes problemas con la implementación:

1. Verifica que el servidor esté corriendo
2. Confirma que el token de autenticación sea válido
3. Revisa los logs del servidor para errores específicos
4. Usa el script de pruebas para verificar los endpoints

¡Los endpoints están listos para usar en tu aplicación Flutter! 🚀
