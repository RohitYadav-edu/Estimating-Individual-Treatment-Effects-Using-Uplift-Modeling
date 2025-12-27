import json
import os
from typing import Any, Dict, List

import joblib
import numpy as np
import pandas as pd

# --- Load model once per container
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'uplift_tlearner_bundle.joblib')
MODEL = joblib.load(MODEL_PATH)
MODEL_TREATED = MODEL['model_treated']
MODEL_CONTROL = MODEL['model_control']
FEATURE_NAMES = MODEL['feature_names']

def _parse_event(event):
    '''API Gateway Case'''
    if isinstance(event, dict) and 'body' in event and event['body']:
        body = event['body']
        if isinstance (body, str):
            return json.loads(body)
        return body
    
    '''Direct invocation case'''
    return event

def _validate_instances(payload):
    if 'instances' not in payload:
        raise ValueError('Missing required key: "instances".')

    instances = payload['instances']
    
    if not isinstance(instances, list):
        raise ValueError('"instances" must be a list.')

    if len(instances) == 0:
        raise ValueError('"instances" must be a non-empty list.')

    for i, row in enumerate(instances):
        if not isinstance(row, dict):
            raise ValueError(f'The "instance" at index {i} must be a JSON object/dict.')

        missing = [f for f in FEATURE_NAMES if f not in row]
        if missing:
            raise ValueError(f'The "instance" at {i} is missing features: {missing}.')
    
    return instances

def _to_feature_matrix(instances: List[Dict[str, Any]]) -> np.ndarray:
    return pd.DataFrame(instances)[FEATURE_NAMES]

def handler(event: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    try:
        payload = _parse_event(event)
        instances = _validate_instances(payload)
        X = _to_feature_matrix(instances)

        p1 = MODEL_TREATED.predict_proba(X)[:, 1]
        p0 = MODEL_CONTROL.predict_proba(X)[:, 1]
        uplift = p1 - p0

        preds = [
            {'p_treated': float(a), 'p_control': float(b), 'uplift': float(c)}
            for a, b, c in zip(p1, p0, uplift)
        ]

        response_body = {
            'predictions': preds, 
            'model': 'tlearner_logreg_v1', 
            'n': len(preds)
        }

        return{
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps(response_body),
        }
    except Exception as e:
        return{
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': str(e)}),
        }