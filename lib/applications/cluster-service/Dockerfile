FROM public.ecr.aws/parallelcluster/pcluster-api:3.2.0


RUN ln -s /tmp  /home/sbx_user1051


COPY cluster_service.py ./

ENTRYPOINT ["/bin/sh","-c","/lambda-entrypoint.sh"] 
CMD ["cluster_service.lambda_handler"]
WORKDIR /var/task

