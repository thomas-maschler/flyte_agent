# Custom Flyte Agent

This is a basic implementation of a custom Flyte agent, task and workflow simulating an async job.

## Sandbox deployment

1. Start the Flyte sandbox:

```shell
flytectl demo start
```


2. Build Docker image and push to sandbox registry

```shell
docker buildx build -t localhost:30000/custom_flyteagent:latest . --load
docker push localhost:30000/custom_flyteagent:latest
```

3. Update agent image in sandbox deployment
```shell
kubectl edit deployment flyteagent -n flyte
```

update image entry as follows:
```yaml
image: localhost:30000/custom_flyteagent:latest
```

4. Restart sandbox deployment
```shell
kubectl rollout restart deployment flyte-sandbox -n flyte
```

5. Execute remote workflow
```shell
pyflyte run --remote --image localhost:30000/custom_flyteagent:latest flyte_agent/custom_workflow.py --input_a='test input' --input_b=123
```