FROM public.ecr.aws/lambda/python:3.12

RUN pip install --no-cache-dir numpy pandas scikit-learn joblib

RUN mkdir -p ${LAMBDA_TASK_ROOT}/models
COPY deploy/handler.py ${LAMBDA_TASK_ROOT}/handler.py
COPY models/uplift_tlearner_bundle.joblib ${LAMBDA_TASK_ROOT}/models/uplift_tlearner_bundle.joblib

CMD ["handler.handler"]
