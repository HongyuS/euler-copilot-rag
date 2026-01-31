FROM  hub.oepkgs.net/neocopilot/data_chain_back_end_base:0.10.0-x86

COPY --chmod=750 ./data_chain /rag-service/data_chain
COPY --chmod=750 ./chat2db /rag-service/chat2db
COPY --chmod=750 ./run.sh /rag-service/

WORKDIR /rag-service

ENV PYTHONPATH /rag-service

USER root

CMD ["/bin/bash", "run.sh"]

