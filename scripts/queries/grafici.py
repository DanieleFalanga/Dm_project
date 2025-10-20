# Conversione delle unità
no_index_df["executiontime_s"] = no_index_df["executiontime_ms"] / 1000
no_index_df["mysqlmemoryused_mb"] = no_index_df["mysqlmemoryused_kb"] / 1024

with_index_df["executiontime_s"] = with_index_df["executiontime_ms"] / 1000
with_index_df["mysqlmemoryused_mb"] = with_index_df["mysqlmemoryused_kb"] / 1024

# --- Query senza indici: Tempo (in secondi) ---
plt.figure(figsize=(10,6))
for query, df_group in no_index_df.groupby("query"):
    plt.plot(df_group["run"], df_group["executiontime_s"], marker='o', label=f"{query}")
plt.title("Query Senza Indici - Tempo di Esecuzione")
plt.xlabel("Run")
plt.ylabel("Tempo di esecuzione (s)")
plt.legend(title="Query")
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()

# --- Query senza indici: Memoria (in MB) ---
plt.figure(figsize=(10,6))
for query, df_group in no_index_df.groupby("query"):
    plt.plot(df_group["run"], df_group["mysqlmemoryused_mb"], marker='o', label=f"{query}")
plt.title("Query Senza Indici - Utilizzo di Memoria")
plt.xlabel("Run")
plt.ylabel("Memoria utilizzata (MB)")
plt.legend(title="Query")
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()

# --- Query con indici: Tempo (in secondi) ---
plt.figure(figsize=(10,6))
for query, df_group in with_index_df.groupby("query"):
    plt.plot(df_group["run"], df_group["executiontime_s"], marker='o', label=f"{query}")
plt.title("Query Con Indici - Tempo di Esecuzione")
plt.xlabel("Run")
plt.ylabel("Tempo di esecuzione (s)")
plt.legend(title="Query")
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()

# --- Query con indici: Memoria (in MB) ---
plt.figure(figsize=(10,6))
for query, df_group in with_index_df.groupby("query"):
    plt.plot(df_group["run"], df_group["mysqlmemoryused_mb"], marker='o', label=f"{query}")
plt.title("Query Con Indici - Utilizzo di Memoria")
plt.xlabel("Run")
plt.ylabel("Memoria utilizzata (MB)")
plt.legend(title="Query")
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()
