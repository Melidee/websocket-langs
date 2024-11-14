#include <http.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

Request *new_request(Method method) {
    Request *request = (Request *)malloc(sizeof(request));
    request->method = method;
    request->path = "";
    request->proto = "http/1.1";
    request->headers = new_headers();
    request->body = "";
    return request;
}

Request *parse_request(char *req, uint32_t size) {
    int i;
    char *method_str, *path, *proto, *headers_str, *body;
    i = strget_sep(req, " ", method_str);
    i = strget_sep(req, " ", path);
    i = strget_sep(req, "\r\n", proto);
    i = strget_sep(req, "\r\n\r\n", headers_str);
    uint32_t body_size = ((size - i) + 1) * sizeof(char);
    body = (char *)malloc(body_size);
    strncpy(body, &req[i], body_size);

    Method method = method_from_str(method_str);
    path[strlen(path) - 1] = '\0';
    proto[strlen(proto) - 2] = '\0';
    Headers *headers = parse_headers(headers_str);

    Request *request = new_request(method);
    request->path = path;
    request->proto = proto;
    request->headers = headers;
    request->body = body;
    free(method_str);
    free(headers_str);
    free(req);
    return request;
}

char *request_to_str(Request *request) {
    return sprintf("%s %s %s\r\n%s\r\n%s", method_strs[request->method],
                   request->path, request->proto,
                   headers_to_str(request->headers), request->body);
}

uint32_t strget_sep(char *req, char *separator, char *dest) {
    uint32_t i = 0;
    while (strncmp(req, separator, strlen(separator)) != 0) {
        i++;
    }
    uint32_t len = i + strlen(separator);
    *dest = (char *)malloc(len * sizeof(char));
    strncpy(dest, req, len);
    dest[len - 1] = '\0';
    req = &req[len];
    return len;
}

Method method_from_str(char *method_str) {
    if (strncmp(method_str, "GET", 3) == 0) {
        return METHOD_GET;
    } else if (strncmp(method_str, "POST", 4) == 0) {
        return METHOD_POST;
    } else if (strncmp(method_str, "PUT", 4) == 0) {
        return METHOD_PUT;
    } else if (strncmp(method_str, "DELETE", 6) == 0) {
        return METHOD_DELETE;
    } else if (strncmp(method_str, "PATCH", 5) == 0) {
        return METHOD_PATCH;
    } else if (strncmp(method_str, "HEAD", 4) == 0) {
        return METHOD_HEAD;
    } else if (strncmp(method_str, "OPTIONS", 7) == 0) {
        return METHOD_OPTIONS;
    } else if (strncmp(method_str, "TRACE", 5) == 0) {
        return METHOD_TRACE;
    } else if (strncmp(method_str, "CONNECT", 7) == 0) {
        return METHOD_CONNECT;
    }
}

Headers *new_headers() {
    Headers *headers = (Headers *)malloc(sizeof(Headers));
    headers->size = 0;
    headers->capacity = 4;
    *headers->keys = (char **)malloc(4 * sizeof(char *));
    *headers->keys = (char **)malloc(4 * sizeof(char *));
    return headers;
}

Headers *parse_headers(char *headers_str) {}

char *headers_to_str(Headers *headers) {}

void append_header(Headers *headers, char *key, char *val) {
    if (headers->capacity == headers->size) {
        *headers->keys = realloc(headers->keys, 2 * headers->capacity);
        *headers->vals = realloc(headers->vals, 2 * headers->capacity);
    };

    headers->keys[headers->size + 1] = key;
    headers->vals[headers->size + 1] = val;
    headers->size++;
}

char *get_header_value(Headers *headers, char *key) {
    for (int32_t i = 0; i <= headers->size; i++) {
        if (strcmp(key, headers->keys[i]) == 0) {
            return headers->vals[i];
        }
    }
    return NULL;
}