/*
 * Developer Live Mode's deliberately tiny Arma extension.
 *
 * It exposes no networking, process execution, shell, directory traversal,
 * or write operation.  On each call it returns the current contents of the
 * one run-scoped command file mounted at the fixed path below.  The mission
 * owns parsing/execution and records every command ID in its RPT.
 */
#include <stdio.h>
#include <errno.h>
#include <string.h>

void RVExtension(char *output, int output_size, const char *function) {
    const char *path = "/run/pontifex/live-control/server.sqf";
    FILE *input;
    size_t count;
    (void)function;
    if (output_size <= 0) return;
    output[0] = '\0';
    input = fopen(path, "rb");
    if (input == NULL) {
        snprintf(output, (size_t)output_size,
                 "diag_log \"PONTIFEX_LIVE|server|INBOX_UNREADABLE|%d\";", errno);
        return;
    }
    count = fread(output, 1, (size_t)output_size - 1, input);
    output[count] = '\0';
    fclose(input);
}
