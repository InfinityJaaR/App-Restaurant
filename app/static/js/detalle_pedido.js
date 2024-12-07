document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('entregarPedidoBtn').addEventListener('click', function() {
        var confirmModal = new bootstrap.Modal(document.getElementById('confirmModal'));
        confirmModal.show();
    });

    document.getElementById('confirmEntregaBtn').addEventListener('click', function() {
        document.getElementById('entregarPedidoForm').submit();
    });
});