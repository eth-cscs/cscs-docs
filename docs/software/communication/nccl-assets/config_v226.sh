export NCCL_VERSION=v2.26.2-1
export AWS_OFI_NCCL_VERSION=v1.14.1
export LIBFABRIC_VERSION=v2.2.0
export NCCL_TEST_VERSION=v2.17.1

# ---------------------------------------------------------------------------
#
#  Critical Values
#
# ---------------------------------------------------------------------------

export NCCL_NET="AWS Libfabric"
export NCCL_NET_GDR_LEVEL=PHB
export FI_MR_CACHE_MONITOR=userfaultfd
export MPICH_GPU_SUPPORT_ENABLED=0

# Enable the "alternative rendezvous configuration" of Slingshot to avoid
# sporadic, catastrophic drops in performance
export FI_CXI_RDZV_PROTO=alt_read
export SBATCH_NETWORK=disable_rdzv_get

# ---------------------------------------------------------------------------
#
#  Recommended Values
#
# ---------------------------------------------------------------------------

export FI_CXI_DEFAULT_CQ_SIZE=131072
export FI_CXI_DEFAULT_TX_SIZE=32768
export FI_CXI_DISABLE_HOST_REGISTER=1
export FI_CXI_RDZV_EAGER_SIZE=0

# ---------------------------------------------------------------------------
#
#  Debugging Values
#
# ---------------------------------------------------------------------------

export NCCL_DEBUG=INFO
export NCCL_DEBUG_SUBSYS=INIT,BOOTSTRAP,ENV,TUNING

# ---------------------------------------------------------------------------
#
#  Enable CSCS NCCL Tuning Plugin
#
# ---------------------------------------------------------------------------

export NCCL_TUNER_PLUGIN=cscs
