ARG BUILD_FROM=alpine:3.22
FROM $BUILD_FROM

# Add env
ENV LANG=C.UTF-8
# Set CUPS environment variables for data persistence
ENV CUPS_DATADIR=/data/cups
ENV CUPS_CACHEDIR=/data/cups/cache
ENV CUPS_LOGDIR=/data/cups/logs
ENV CUPS_STATEDIR=/data/cups/state
ENV CUPS_SERVERROOT=/data/cups/config

# Setup base
RUN \
    apk update && \
    apk add --no-cache \
        cups \
        cups-filters \
        ghostscript \
        libjpeg-turbo \
        net-snmp \
        gcompat \
        libstdc++ \
        dpkg \
        jq && \
    for pkg in \
        epson-inkjet-printer-escpr \
        hplip \
        gutenprint \
        foomatic-db \
        foomatic-db-ppds; do \
        apk add --no-cache "${pkg}" || echo "Optional package not available on this architecture/release: ${pkg}"; \
    done

# Copy data
COPY rootfs /

# Expose CUPS web interface port
EXPOSE 631

HEALTHCHECK \
    CMD lpstat -r || exit 1