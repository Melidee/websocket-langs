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
} Status;

typedef struct {
    uint32_t size;
    uint32_t capacity;
    char** keys;
    char** vals;
} Headers;