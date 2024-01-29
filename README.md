[RAG](https://research.ibm.com/blog/retrieval-augmented-generation-RAG) for chatting with infrastructure managed with [Terraform](https://www.terraform.io/). Features:

1. Simple Cli pattern
2. Choice of either OpenAI's [Assistants](https://platform.openai.com/docs/assistants/overview) API or a locally running in-memory RAG with either GPT-4 or [CodeLlama-34](https://huggingface.co/codellama/CodeLlama-34b-hf) as the LLM. 


# Usage
1. Install [Pipenv](https://docs.pipenv.org/install/#installing-pipenv), if not already installed.
2. Install dependencies with `pipenv install`.
3. Start the virtual environment shell with `pipenv shell`.
4. Set environment variables `OPENAI_API_KEY` and `REPLICATE_API_TOKEN` with the OpenAI API key and the [Replicate](https://replicate.com/) API token respectively. (The replicate API token is required for `codellama-34b` inferences and hence optional.)
5. Run `python3 cli.py --help` to for the cli usage options.
6. For a local in-memory RAG with `gpt-4` as the llm, and a top-level directory `~/infra` containing the terraform state files, start the cli with `python3 cli.py -m gpt-4 -d ~/infra` and start chatting away!
7. For a RAG using the OpenAI Assistants API, start the cli with `python3 cli.py -a -d ~/infra` and start chatting away!

# Example Usage

1. Go through this [tutorial](https://developer.hashicorp.com/terraform/tutorials/networking/multicloud-kubernetes?ajs_aid=7e134de7-1e00-4e81-8ac4-13bd8f9acd8a&product_intent=terraform#clean-up-resources) for a federated muticloud kubernetes clusters deployment.

## Assistants

1. Start cli with Assistants: `python3 cli.py -a -d ~/learn-terraform-multicloud-kubernetes`.
2. Example session:

```
> what are the details of the mesh gateway connecting eks and aks?
⠴ generating answer


⠧ The Consul mesh gateway that connects the EKS and AKS clusters is configured with the help of a Kubernetes secret named "eks_federation_secret."
This secret is located in the EKS cluster and is managed by a Terraform provider targeted for EKS `provider["registry.terraform.io/hashicorp/kubernetes"].eks`【42†source】.

This federation secret likely contains the necessary certificates (including CA certificates and potentially others)
for establishing secure and trusted communication between the two clusters' Consul mesh gateways.
The characteristics of the mesh gateway itself in terms of replicas, resources, and other configurations
are not explicitly detailed in the provided excerpt from the Terraform configuration.

If you need more specific details regarding the actual deployment and configuration of the mesh gateway resources (e.g., CPU, memory, environmental variables),
additional information would be required from the Terraform files that describe the mesh gateway infrastructure or the configuration applied by the Helm chart
for Consul in both EKS and AKS. Unfortunately, a tool error prevents quoting the precise section of the document that describes the secret's creation and link with the mesh gateway.
> how does aks load the federation secret from eks?
⠇ generating answer


⠙ generating answerThe AKS cluster loads the federation secret from the EKS cluster through a two-step Terraform data flow:

1. A Terraform `data` resource of type `kubernetes_secret` named `eks_federation_secret` is used to read the existing federation secret from the EKS cluster.
2. A Terraform `kubernetes_secret` resource named `aks_federation_secret` is then created in the AKS cluster using the data obtained from the `eks_federation_secret`.

This process ensures that the AKS cluster has the same federation secret as the EKS cluster, facilitating the federation and allowing for secure communication between the clusters' Consul instances【76†source】.~
```


## Local RAG

1. Start cli with Assistants: `python3 cli.py -m gpt-4 -d ~/learn-terraform-multicloud-kubernetes`.
2. Example session:

```
Welcome!
Please specify what you would like to ask from your terraform templates. >what are the details of the consul mesh gateway connecting eks and aks?
The Consul mesh gateway that connects the EKS and AKS clusters is part of the Consul service mesh setup. The mesh gateway facilitates communication between services in different Kubernetes clusters or different datacenters by routing the traffic between them. Here are the details based on the provided context:

- **Helm Chart**: The mesh gateway is deployed using the Consul Helm chart, which is a package that contains all the necessary resources and configurations to deploy Consul on Kubernetes.
- **Chart Version**: The version of the Consul Helm chart used is `1.2.0`.
- **Datacenters**: The Consul service mesh is set up with federation between two datacenters. The provided context indicates that there are two Helm releases for Consul, one for each datacenter (`consul_dc1` and `consul_dc2`). The `dc2` datacenter is specifically mentioned in the context of the AKS cluster.
- **Federation**: Federation is enabled, allowing the two Consul datacenters to communicate with each other. This is indicated by the `global.federation.enabled: true` setting in the Helm release values.
- **TLS**: TLS is enabled for the mesh gateway, which ensures that the communication between the datacenters is secure. The TLS certificates are stored in Kubernetes secrets (`consul-federation`) and referenced in the Helm release values.
- **Mesh Gateway Configuration**: The mesh gateway is enabled with `meshGateway.enabled: true` and is configured to have `1` replica, which means there will be one instance of the mesh gateway pod running.
- **Connect Inject**: The `connectInject` feature is enabled, which automatically injects the Consul sidecar proxies into pods, enabling them to join the service mesh.
- **Controller**: The Consul controller is enabled, which is responsible for configuring the mesh according to the Consul custom resources defined in Kubernetes.

The mesh gateway is a critical component for cross-cluster communication in a Consul service mesh. It allows services in different Kubernetes clusters to discover and communicate with each other as if they were in the same network, without requiring pods to have direct network access across cluster boundaries.
> how does aks load the federation secret from eks?
How does Azure Kubernetes Service (AKS) load the federation secret from Amazon Elastic Kubernetes Service (EKS)?The Azure Kubernetes Service (AKS) does not directly load secrets from Amazon Elastic Kubernetes Service (EKS). However, in a multi-cloud setup where both AKS and EKS are used, it is possible to share secrets between the two using a synchronization process or by manually copying the secret data.

Based on the provided context, it seems that Terraform is being used to manage the infrastructure, which includes AKS and EKS clusters. The federation secret could be shared between the two services by defining it in Terraform and applying it to both clusters.

Here's a high-level overview of how this could be achieved:

1. Define the Kubernetes secret in Terraform using the `kubernetes_secret` resource type.
2. Apply the Terraform configuration to both the AKS and EKS clusters, ensuring that the secret is created in both clusters with the same data.
3. Use the secret within the clusters as needed by referencing it in the Kubernetes workloads (e.g., pods, deployments).

In the provided context, there are two `kubernetes_secret` resources defined, one for AKS (`aks_federation_secret`) and one for EKS (`eks_federation_secret`). Both secrets contain the same data, including `caCert`, `caKey`, and `serverConfigJSON`. This suggests that the same federation secret is being managed for both clusters, allowing them to share the same configuration for federation purposes.

The actual synchronization or copying of the secret data is handled by Terraform when it applies the configuration to the respective clusters. There is no direct communication between AKS and EKS for loading the secret; instead, Terraform ensures that both clusters have the required secret by applying the same configuration to both.
>
```