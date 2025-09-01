# 🔗 Integración con tu HttpService Existente

## 📋 Resumen

Esta guía te muestra cómo integrar el servicio de pagos con imágenes usando tu `HttpService` existente, manteniendo la misma estructura y patrones que ya usas.

## 🎯 Tu HttpService Actual

Tu `HttpService` ya tiene todo lo necesario:
- ✅ **POST multipart** para archivos
- ✅ **Manejo de tokens** automático
- ✅ **Manejo de errores** robusto
- ✅ **CORS handling** para web
- ✅ **Timeout** configurado

## 🔧 Implementación del Servicio de Pagos

### **1. Crear el archivo `lib/services/payment_service.dart`**

```dart
import 'dart:typed_data';
import 'http_service.dart';

// Modelo de respuesta API (compatible con tu estructura)
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

// Servicio de pagos integrado con tu HttpService
class PaymentService {
  final HttpService _httpService;

  PaymentService({HttpService? httpService}) 
    : _httpService = httpService ?? HttpService();

  /// Subir solo imagen de pago (ENDPOINT FUNCIONANDO)
  Future<ApiResponse<Map<String, dynamic>>> uploadPaymentImage({
    required String contractId,
    required String reference,
    required Uint8List imageFile,
    String? imageFilename,
  }) async {
    try {
      final token = await _httpService.getAuthorizationToken();
      
      final fields = {
        'contract_id': contractId,
        'reference': reference,
      };

      final files = {
        'image_file': imageFile.toList(),
      };

      final fileNames = {
        'image_file': imageFilename ?? '$reference.jpg',
      };

      final response = await _httpService.postMultipart<Map<String, dynamic>>(
        '/loan-payments/upload-payment-image',
        fields: fields,
        files: files,
        fileNames: fileNames,
        token: token,
      );

      // Verificar si la respuesta indica éxito
      final success = response['success'] ?? false;
      
      if (success) {
        final message = response['message'] ?? 'Imagen subida exitosamente';
        return ApiResponse.successResponse(response, message: message);
      } else {
        final errorMessage = response['message'] ?? 'Error al subir imagen';
        return ApiResponse.errorResponse(errorMessage);
      }
    } catch (e) {
      if (e is ApiException) {
        return ApiResponse.errorResponse(e.message);
      }
      return ApiResponse.errorResponse('Error al subir imagen: $e');
    }
  }

  /// Registrar transacción sin imagen (ENDPOINT FUNCIONANDO)
  Future<ApiResponse<Map<String, dynamic>>> registerTransaction(
    PaymentData paymentData,
  ) async {
    try {
      final token = await _httpService.getAuthorizationToken();
      
      final response = await _httpService.post<Map<String, dynamic>>(
        '/loan-payments/register-transaction',
        body: paymentData.toJson(),
        token: token,
      );

      // Verificar si la respuesta indica éxito
      final success = response['success'] ?? false;
      
      if (success) {
        final message = response['message'] ?? 'Transacción registrada exitosamente';
        return ApiResponse.successResponse(response, message: message);
      } else {
        final errorMessage = response['message'] ?? 'Error al registrar transacción';
        return ApiResponse.errorResponse(errorMessage);
      }
    } catch (e) {
      if (e is ApiException) {
        return ApiResponse.errorResponse(e.message);
      }
      return ApiResponse.errorResponse('Error al registrar transacción: $e');
    }
  }

  /// Método principal que decide qué endpoint usar
  Future<ApiResponse<Map<String, dynamic>>> registerPayment(
    PaymentData paymentData,
  ) async {
    try {
      // Si tiene imagen, subir imagen primero y luego registrar transacción
      if (paymentData.imageFile != null) {
        print('🖼️ Pago con imagen detectado, subiendo imagen primero...');
        
        // Subir imagen
        final imageResult = await uploadPaymentImage(
          contractId: paymentData.contractLoanId.toString(),
          reference: paymentData.reference,
          imageFile: paymentData.imageFile!,
          imageFilename: paymentData.imageFilename,
        );

        if (!imageResult.success) {
          return imageResult;
        }

        // Luego registrar transacción (sin imagen)
        print('📝 Registrando transacción...');
        return await registerTransaction(paymentData);
      } else {
        // Si no tiene imagen, usar el endpoint de transacción simple
        print('📝 Pago sin imagen, usando endpoint de transacción...');
        return await registerTransaction(paymentData);
      }
    } catch (e) {
      if (e is ApiException) {
        return ApiResponse.errorResponse(e.message);
      }
      return ApiResponse.errorResponse('Error al registrar pago: $e');
    }
  }
}

// Adaptador para mantener compatibilidad con tu código original
class PaymentServiceAdapter {
  final PaymentService _paymentService;

  PaymentServiceAdapter({HttpService? httpService}) 
    : _paymentService = PaymentService(httpService: httpService);

  /// Método adaptado de tu código original
  Future<ApiResponse<String>> registerPayment(Map<String, dynamic> paymentData) async {
    try {
      print('🚀 Iniciando registro de pago...');

      // Verificar si hay imagen
      final hasImageFile = paymentData.containsKey('image_file') &&
          paymentData['image_file'] is List<int>;

      // Convertir datos a PaymentData
      final paymentDataObj = PaymentData(
        contractLoanId: paymentData['contract_loan_id'] as int,
        amount: (paymentData['amount'] as num).toDouble(),
        paymentMethod: paymentData['payment_method'] as String? ?? 'Bank Transfer',
        reference: paymentData['reference'] as String,
        notes: paymentData['notes'] as String?,
        transactionDate: paymentData['transaction_date'] as String?,
        imageFile: hasImageFile ? Uint8List.fromList(paymentData['image_file'] as List<int>) : null,
        imageFilename: paymentData['image_filename'] as String?,
      );

      // Usar el servicio de pagos
      final result = await _paymentService.registerPayment(paymentDataObj);

      if (result.success) {
        return ApiResponse.successResponse('success', message: result.message);
      } else {
        return ApiResponse.errorResponse(result.error ?? 'Error desconocido');
      }
    } catch (e) {
      print('💥 Exception in registerPayment: $e');
      return ApiResponse.errorResponse('Error al registrar el pago: $e');
    }
  }

  /// Método para subir solo imagen
  Future<ApiResponse<String>> uploadPaymentImage({
    required String contractId,
    required String reference,
    required List<int> imageBytes,
    String? imageFilename,
  }) async {
    try {
      final result = await _paymentService.uploadPaymentImage(
        contractId: contractId,
        reference: reference,
        imageFile: Uint8List.fromList(imageBytes),
        imageFilename: imageFilename,
      );

      if (result.success) {
        return ApiResponse.successResponse('success', message: result.message);
      } else {
        return ApiResponse.errorResponse(result.error ?? 'Error desconocido');
      }
    } catch (e) {
      print('💥 Exception in uploadPaymentImage: $e');
      return ApiResponse.errorResponse('Error al subir imagen: $e');
    }
  }
}
```

### **2. Agregar ImagePicker (opcional)**

Si quieres usar ImagePicker, agrega la dependencia:

```yaml
# pubspec.yaml
dependencies:
  image_picker: ^1.0.4
```

Y crea el servicio con ImagePicker:

```dart
// Agregar al archivo payment_service.dart
import 'package:image_picker/image_picker.dart';

// Servicio con ImagePicker integrado
class PaymentWithImagePicker {
  final PaymentServiceAdapter _adapter;
  final ImagePicker _picker = ImagePicker();

  PaymentWithImagePicker({HttpService? httpService}) 
    : _adapter = PaymentServiceAdapter(httpService: httpService);

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
      print('💥 Error en selectImageAndRegisterPayment: $e');
      return ApiResponse.errorResponse('Error: $e');
    }
  }

  /// Tomar foto y registrar pago
  Future<ApiResponse<String>> takePhotoAndRegisterPayment({
    required int contractLoanId,
    required double amount,
    required String reference,
    String? notes,
  }) async {
    try {
      // Tomar foto
      final XFile? image = await _picker.pickImage(
        source: ImageSource.camera,
        maxWidth: 1024,
        maxHeight: 1024,
        imageQuality: 85,
      );

      if (image == null) {
        return ApiResponse.errorResponse('No se tomó ninguna foto');
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
      print('💥 Error en takePhotoAndRegisterPayment: $e');
      return ApiResponse.errorResponse('Error: $e');
    }
  }
}
```

## 📱 Ejemplos de Uso

### **Ejemplo 1: Usar tu método original**

```dart
// En tu servicio existente o donde lo uses
import 'services/payment_service.dart';

class YourExistingService {
  final HttpService _httpService = HttpService();
  late final PaymentServiceAdapter _paymentAdapter;

  YourExistingService() {
    _paymentAdapter = PaymentServiceAdapter(httpService: _httpService);
  }

  // Tu método original - NO CAMBIA NADA
  Future<ApiResponse<String>> registerPayment(Map<String, dynamic> paymentData) async {
    // Este método usa tu HttpService internamente
    return await _paymentAdapter.registerPayment(paymentData);
  }
}

// Uso exactamente igual que antes
final service = YourExistingService();

final paymentData = {
  'contract_loan_id': 123,
  'amount': 1500.00,
  'payment_method': 'Bank Transfer',
  'reference': 'PAYMENT_001',
  'notes': 'Pago mensual con voucher',
  'image_file': imageBytes, // List<int> de la imagen
  'image_filename': 'voucher.jpg',
};

final result = await service.registerPayment(paymentData);
if (result.success) {
  print('✅ Pago registrado: ${result.message}');
} else {
  print('❌ Error: ${result.error}');
}
```

### **Ejemplo 2: Con ImagePicker**

```dart
import 'services/payment_service.dart';

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
    // Usa tu HttpService existente
    final httpService = HttpService();
    _paymentService = PaymentWithImagePicker(httpService: httpService);
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

### **Ejemplo 3: Uso directo del servicio**

```dart
import 'services/payment_service.dart';

void exampleUsage() async {
  // Usar tu HttpService existente
  final httpService = HttpService();
  
  // Configurar servicio de pagos
  final paymentService = PaymentService(httpService: httpService);

  try {
    // Ejemplo 1: Pago con imagen
    final paymentWithImage = PaymentData(
      contractLoanId: 123,
      amount: 1500.00,
      reference: 'PAYMENT_001',
      notes: 'Pago mensual con voucher',
      imageFile: Uint8List.fromList([1, 2, 3, 4, 5]), // Datos de imagen reales
      imageFilename: 'voucher.jpg',
    );

    final result1 = await paymentService.registerPayment(paymentWithImage);
    if (result1.success) {
      print('✅ Pago con imagen registrado: ${result1.message}');
    } else {
      print('❌ Error: ${result1.error}');
    }

    // Ejemplo 2: Pago sin imagen
    final paymentWithoutImage = PaymentData(
      contractLoanId: 123,
      amount: 1000.00,
      reference: 'PAYMENT_002',
      notes: 'Pago sin voucher',
    );

    final result2 = await paymentService.registerPayment(paymentWithoutImage);
    if (result2.success) {
      print('✅ Pago sin imagen registrado: ${result2.message}');
    } else {
      print('❌ Error: ${result2.error}');
    }

  } catch (e) {
    print('💥 Error en ejemplo: $e');
  }
}
```

## 🎯 Ventajas de esta Integración

1. **✅ Compatibilidad Total**: Usa tu `HttpService` existente
2. **✅ Sin Cambios**: Tu código original no cambia
3. **✅ Mismo Patrón**: Mantiene tu estructura de manejo de errores
4. **✅ Tokens Automáticos**: Usa tu sistema de autenticación
5. **✅ CORS Handling**: Aprovecha tu manejo de CORS
6. **✅ Timeout**: Usa tu configuración de timeout
7. **✅ Logs**: Mantiene tus logs y debugging

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

## 🧪 Endpoints Probados

- ✅ **`/loan-payments/upload-payment-image`** - Subir imagen
- ✅ **`/loan-payments/register-transaction`** - Registrar transacción

## 🚀 Resumen

Con esta integración:

1. **No cambias nada** en tu código existente
2. **Usas tu HttpService** con toda su funcionalidad
3. **Mantienes tu estructura** de manejo de errores
4. **Aprovechas** tu sistema de autenticación
5. **Conservas** tu manejo de CORS y timeout

¡Tu servicio está listo para usar con los endpoints de pagos con imágenes! 🎉
