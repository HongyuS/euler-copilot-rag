FROM  hub.oepkgs.net/neocopilot/data_chain_back_end_base:0.9.6-x86

COPY --chmod=750 ./ /rag-service/
WORKDIR /rag-service

ENV PYTHONPATH /rag-service

USER root

CMD ["/bin/bash", "run.sh"]

