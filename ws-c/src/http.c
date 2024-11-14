#include <stdint.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    Method method;
    char *path;
    uint8_t proto_major;
    uint8_t proto_minor;
    Headers *headers;
    char *body;

} Request;

typedef enum {
    METHOD_GET,
    METHOD_POST,
    METHOD_PUT,
    METHOD_DELETE,
    METHOD_PATCH,
    METHOD_HEAD,
    METHOD_OPTIONS,
    METHOD_TRACE,
    METHOD_CONNECT,
} Method;

typedef struct {
    uint8_t proto_major;
    uint8_t proto_minor;
    Status status;
    Headers *Headers;
    char *body;
} Response;

typedef enum {
    HTTP_100_CONTINUE,
    HTTP_101_SWITCHING_PROTOCOLS,
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_202_ACCEPTED,
    HTTP_203_NON_AUTHORITATIVE_INFORMATION,
    HTTP_204_NO_CONTENT,
    HTTP_205_RESET_CONTENT,
    HTTP_206_PARTIAL_CONTENT,
    HTTP_300_MULTIPLE_CHOICES,
    HTTP_301_MOVED_PERMANENTLY,
    HTTP_302_FOUND,
    HTTP_303_SEE_OTHER,
    HTTP_304_NOT_MODIFIED,
    HTTP_305_USE_PROXY,
    HTTP_307_TEMPORARY_REDIRECT,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_402_PAYMENT_REQUIRED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_405_METHOD_NOT_ALLOWED,
    HTTP_406_NOT_ACCEPTABLE,
    HTTP_407_PROXY_AUTHENTICATION_REQUIRED,
    HTTP_408_REQUEST_TIMEOUT,
    HTTP_409_CONFLICT,
    HTTP_410_GONE,
    HTTP_411_LENGTH_REQUIRED,
    HTTP_412_PRECONDITION_FAILED,
    HTTP_413_REQUEST_ENTITY_TOO_LARGE,
    HTTP_414_REQUEST_URI_TOO_LONG,
    HTTP_415_UNSUPPORTED_MEDIA_TYPE,
    HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
    HTTP_417_EXPECTATION_FAILED,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_423_LOCKED,
    HTTP_424_FAILED_DEPENDENCY,
    HTTP_426_UPGRADE_REQUIRED,
    HTTP_428_PRECONDITION_REQUIRED,
    HTTP_429_TOO_MANY_REQUESTS,
    HTTP_431_REQUEST_HEADER_FIELDS_TOO_LARGE,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_501_NOT_IMPLEMENTED,
    HTTP_502_BAD_GATEWAY,
    HTTP_503_SERVICE_UNAVAILABLE,
    HTTP_504_GATEWAY_TIMEOUT,
    HTTP_505_HTTP_VERSION_NOT_SUPPORTED,
    HTTP_506_VARIANT_ALSO_NEGOTIATES,
    HTTP_507_INSUFFICIENT_STORAGE,
    HTTP_508_LOOP_DETECTED,
    HTTP_510_NOT_EXTENDED,
    HTTP_511_NETWORK_AUTHENTICATION_REQUIRED,
} Status;

typedef struct {
    uint32_t size;
    uint32_t capacity;
    char **keys;
    char **vals;
} Headers;

Headers *new_headers() {
    Headers *headers = (Headers *)malloc(sizeof(Headers));
    headers->size = 0;
    headers->capacity = 4;
    *headers->keys = (char**)malloc(4 * sizeof(char*));
    *headers->keys = (char**)malloc(4 * sizeof(char*));
    return headers;
}

void append_header(Headers *headers, char *key, char *val) {
    if (headers->capacity == headers->size) {
        *headers->keys =
            realloc(headers->keys, 2 * headers->capacity);
        *headers->vals =
            realloc(headers->vals, 2 * headers->capacity);
    };

    headers->keys[headers->size+1] = key;
    headers->vals[headers->size+1] = val;
    headers->size++;
}

char* get_header_value(Headers *headers, char *key) {
    for (uint32_t i = 0; i <= headers->size; i++) {
        if (strcmp(key, headers->keys[i]) == 0) {
            return headers->vals[i];
        }
    }
    return NULL;
}