/* =========================================================
   charts.js
   Dashboards Financeiros — Barbearia SaaS
   ========================================================= */

/* ---------------------------------------------------------
   CONFIGURAÇÃO GLOBAL (PADRÃO PREMIUM)
--------------------------------------------------------- */
Chart.defaults.font.family = "'Poppins', sans-serif";
Chart.defaults.color = "#cfcfcf";
Chart.defaults.plugins.legend.position = "bottom";

/* ---------------------------------------------------------
   UTILIDADES
--------------------------------------------------------- */
function formatCurrency(value) {
    return "R$ " + value.toLocaleString("pt-BR", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

/* ---------------------------------------------------------
   GRÁFICO FATURAMENTO x DESPESAS x LUCRO
--------------------------------------------------------- */
function renderRevenueExpenseProfitChart(ctxId, labels, revenue, expenses, profit) {

    const ctx = document.getElementById(ctxId);
    if (!ctx) return;

    new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Faturamento",
                    data: revenue,
                    backgroundColor: "#f1c40f"
                },
                {
                    label: "Despesas",
                    data: expenses,
                    backgroundColor: "#ff4d4d"
                },
                {
                    label: "Lucro",
                    data: profit,
                    backgroundColor: "#2ecc71"
                }
            ]
        },
        options: {
            responsive: true,
            interaction: {
                mode: "index",
                intersect: false
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function (value) {
                            return formatCurrency(value);
                        }
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return context.dataset.label + ": " +
                                formatCurrency(context.raw);
                        }
                    }
                }
            }
        }
    });
}

/* ---------------------------------------------------------
   GRÁFICO DE LINHA — FATURAMENTO MENSAL
--------------------------------------------------------- */
function renderRevenueLineChart(ctxId, labels, values) {

    const ctx = document.getElementById(ctxId);
    if (!ctx) return;

    new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [{
                label: "Faturamento",
                data: values,
                borderColor: "#f1c40f",
                backgroundColor: "rgba(241, 196, 15, 0.15)",
                tension: 0.4,
                fill: true,
                pointRadius: 4
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    ticks: {
                        callback: value => formatCurrency(value)
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: ctx => formatCurrency(ctx.raw)
                    }
                }
            }
        }
    });
}

/* ---------------------------------------------------------
   GRÁFICO DE PIZZA — DESPESAS POR CATEGORIA
--------------------------------------------------------- */
function renderExpenseCategoryChart(ctxId, labels, values) {

    const ctx = document.getElementById(ctxId);
    if (!ctx) return;

    new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: [
                    "#ff4d4d",
                    "#e67e22",
                    "#9b59b6",
                    "#3498db",
                    "#1abc9c",
                    "#95a5a6"
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function (ctx) {
                            return ctx.label + ": " +
                                formatCurrency(ctx.raw);
                        }
                    }
                }
            }
        }
    });
}

/* ---------------------------------------------------------
   GRÁFICO DE CAIXA — ABERTURA x FECHAMENTO
--------------------------------------------------------- */
function renderCashFlowChart(ctxId, labels, openValues, closeValues) {

    const ctx = document.getElementById(ctxId);
    if (!ctx) return;

    new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Abertura de Caixa",
                    data: openValues,
                    borderColor: "#3498db",
                    tension: 0.3
                },
                {
                    label: "Fechamento de Caixa",
                    data: closeValues,
                    borderColor: "#2ecc71",
                    tension: 0.3
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    ticks: {
                        callback: value => formatCurrency(value)
                    }
                }
            }
        }
    });
}

/* ---------------------------------------------------------
   EXPORTA FUNÇÕES (CASO USE MODULES)
--------------------------------------------------------- */
window.renderRevenueExpenseProfitChart = renderRevenueExpenseProfitChart;
window.renderRevenueLineChart = renderRevenueLineChart;
window.renderExpenseCategoryChart = renderExpenseCategoryChart;
window.renderCashFlowChart = renderCashFlowChart;
