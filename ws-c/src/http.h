typedef struct {
    Method method;
    char *path;
    char *proto;
    Headers *headers;
    char *body;
} Request;

Request *new_request(Method method);

Request *parse_request(char *req, uint32_t size);

char *request_to_str(Request *request);

uint32_t strget_sep(char *req, char *separator, char *dest);

typedef enum {
    METHOD_GET = 0,
    METHOD_POST,
    METHOD_PUT,
    METHOD_DELETE,
    METHOD_PATCH,
    METHOD_HEAD,
    METHOD_OPTIONS,
    METHOD_TRACE,
    METHOD_CONNECT,
} Method;

Method method_from_str(char *method_str);

static const char *method_strs[] = {"GET",     "POST",  "PUT",
                                    "DELETE",  "PATCH", "HEAD",
                                    "OPTIONS", "TRACE", "CONNECT"};

typedef struct {
    uint8_t proto_major;
    uint8_t proto_minor;
    Status status;
    Headers *Headers;
    char *body;
} Response;

typedef enum {
    HTTP_100_CONTINUE = 0,
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

static const char *method_strs[] = {
    "100 Continue",
    "101 Switching Protocols",
    "200 OK",
    "201 Created",
    "202 Accepted",
    "203 Non-Authoritative Information",
    "204 No Content",
    "205 Reset Content",
    "206 Partial Content",
    "300 Multiple Choices",
    "301 Moved Permanently",
    "302 Found",
    "303 See Other",
    "304 Not Modified",
    "305 Use Proxy",
    "307 Temporary Redirect",
    "400 Bad Request",
    "401 Unauthorized",
    "402 Payment Required",
    "403 Forbidden",
    "404 Not Found",
    "405 Method Not Allowed",
    "406 Not Acceptable",
    "407 Proxy Authentication Required",
    "408 Request Timeout",
    "409 Conflict",
    "410 Gone",
    "411 Length Required",
    "412 Precondition Failed",
    "413 Request Entity Too Large",
    "414 Request-URI Too Long",
    "415 Unsupported Media Type",
    "416 Requested Range Not Satisfiable",
    "417 Expectation Failed",
    "422 Unprocessable Entity",
    "423 Locked",
    "424 Failed Dependency",
    "426 Upgrade Required",
    "428 Precondition Required",
    "429 Too Many Requests",
    "431 Request Header Fields Too Large",
    "500 Internal Server Error",
    "501 Not Implemented",
    "502 Bad Gateway",
    "503 Service Unavailable",
    "504 Gateway Timeout",
    "505 HTTP Version Not Supported",
    "506 Variant Also Negotiates",
    "507 Insufficient Storage",
    "508 Loop Detected",
    "510 Not Extended",
    "511 Network Authentication Required",
};

typedef struct {
    uint32_t size;
    uint32_t capacity;
    char **keys;
    char **vals;
} Headers;

Headers *new_headers();

Headers *parse_headers(char *headers_str);

char *headers_to_str(Headers *headers);

void append_header(Headers *headers, char *key, char *val);

char *get_header_value(Headers *headers, char *key);