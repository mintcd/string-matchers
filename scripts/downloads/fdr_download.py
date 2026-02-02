"""FDR (Fast Dictionary-based Regular expression) downloader from Hyperscan."""

import urllib.request
from pathlib import Path

# Hyperscan GitHub repository configuration
HYPERSCAN_REPO = "https://raw.githubusercontent.com/intel/hyperscan/master"
HYPERSCAN_SRC = f"{HYPERSCAN_REPO}/src"

# Files to download from Hyperscan repository
FDR_FILES = {
    # FDR core runtime files
    "src/fdr/fdr/fdr.c": f"{HYPERSCAN_SRC}/src/fdr/fdr.c",
    "src/fdr/fdr/fdr.h": f"{HYPERSCAN_SRC}/src/fdr/fdr.h",
    "src/fdr/fdr/fdr_internal.h": f"{HYPERSCAN_SRC}/src/fdr/fdr_internal.h",
    "src/fdr/fdr/fdr_loadval.h": f"{HYPERSCAN_SRC}/src/fdr/fdr_loadval.h",
    "src/fdr/fdr/fdr_confirm.h": f"{HYPERSCAN_SRC}/src/fdr/fdr_confirm.h",
    "src/fdr/fdr/fdr_confirm_runtime.h": f"{HYPERSCAN_SRC}/src/fdr/fdr_confirm_runtime.h",
    
    # FDR compilation files
    "src/fdr/fdr/fdr_compile.cpp": f"{HYPERSCAN_SRC}/src/fdr/fdr_compile.cpp",
    "src/fdr/fdr/fdr_compile.h": f"{HYPERSCAN_SRC}/src/fdr/fdr_compile.h",
    "src/fdr/fdr/fdr_compile_internal.h": f"{HYPERSCAN_SRC}/src/fdr/fdr_compile_internal.h",
    "src/fdr/fdr/fdr_compile_util.cpp": f"{HYPERSCAN_SRC}/src/fdr/fdr_compile_util.cpp",
    "src/fdr/fdr/fdr_confirm_compile.cpp": f"{HYPERSCAN_SRC}/src/fdr/fdr_confirm_compile.cpp",
    
    # TEDDY engine files
    "src/fdr/fdr/teddy.c": f"{HYPERSCAN_SRC}/src/fdr/teddy.c",
    "src/fdr/fdr/teddy.h": f"{HYPERSCAN_SRC}/src/fdr/teddy.h",
    "src/fdr/fdr/teddy_avx2.c": f"{HYPERSCAN_SRC}/src/fdr/teddy_avx2.c",
    "src/fdr/fdr/teddy_internal.h": f"{HYPERSCAN_SRC}/src/fdr/teddy_internal.h",
    "src/fdr/fdr/teddy_runtime_common.h": f"{HYPERSCAN_SRC}/src/fdr/teddy_runtime_common.h",
    "src/fdr/fdr/teddy_compile.cpp": f"{HYPERSCAN_SRC}/src/fdr/teddy_compile.cpp",
    "src/fdr/fdr/teddy_compile.h": f"{HYPERSCAN_SRC}/src/fdr/teddy_compile.h",
    
    # Engine description files
    "src/fdr/fdr/engine_description.cpp": f"{HYPERSCAN_SRC}/src/fdr/engine_description.cpp",
    "src/fdr/fdr/engine_description.h": f"{HYPERSCAN_SRC}/src/fdr/engine_description.h",
    "src/fdr/fdr/fdr_engine_description.cpp": f"{HYPERSCAN_SRC}/src/fdr/fdr_engine_description.cpp",
    "src/fdr/fdr/fdr_engine_description.h": f"{HYPERSCAN_SRC}/src/fdr/fdr_engine_description.h",
    "src/fdr/fdr/teddy_engine_description.cpp": f"{HYPERSCAN_SRC}/src/fdr/teddy_engine_description.cpp",
    "src/fdr/fdr/teddy_engine_description.h": f"{HYPERSCAN_SRC}/src/fdr/teddy_engine_description.h",
    
    # Flood detection files
    "src/fdr/fdr/flood_compile.cpp": f"{HYPERSCAN_SRC}/src/fdr/flood_compile.cpp",
    "src/fdr/fdr/flood_runtime.h": f"{HYPERSCAN_SRC}/src/fdr/flood_runtime.h",
    
    # Core Hyperscan files
    "src/fdr/grey.cpp": f"{HYPERSCAN_SRC}/grey.cpp",
    "src/fdr/grey.h": f"{HYPERSCAN_SRC}/grey.h",
    "src/fdr/ue2common.h": f"{HYPERSCAN_SRC}/ue2common.h",
    "src/fdr/hs_common.h": f"{HYPERSCAN_SRC}/hs_common.h",
    "src/fdr/hs_compile.h": f"{HYPERSCAN_SRC}/hs_compile.h",
    "src/fdr/hs.h": f"{HYPERSCAN_SRC}/hs.h",
    "src/fdr/hs_runtime.h": f"{HYPERSCAN_SRC}/hs_runtime.h",
    "src/fdr/hs_internal.h": f"{HYPERSCAN_SRC}/hs_internal.h",
    "src/fdr/hs_version.h.in": f"{HYPERSCAN_SRC}/hs_version.h.in",
    "src/fdr/cmake/config.h.in": f"{HYPERSCAN_REPO}/cmake/config.h.in",
    "src/fdr/scratch.h": f"{HYPERSCAN_SRC}/scratch.h",
    "src/fdr/scratch.c": f"{HYPERSCAN_SRC}/scratch.c",
    "src/fdr/alloc.c": f"{HYPERSCAN_SRC}/alloc.c",
    "src/fdr/allocator.h": f"{HYPERSCAN_SRC}/allocator.h",
    "src/fdr/state.h": f"{HYPERSCAN_SRC}/state.h",
    "src/fdr/database.h": f"{HYPERSCAN_SRC}/database.h",
    "src/fdr/database.c": f"{HYPERSCAN_SRC}/database.c",
    "src/fdr/crc32.h": f"{HYPERSCAN_SRC}/crc32.h",
    "src/fdr/crc32.c": f"{HYPERSCAN_SRC}/crc32.c",
    "src/fdr/compiler/compiler.h": f"{HYPERSCAN_SRC}/compiler/compiler.h",
    
    # HWLM (Hardware Literal Matcher) files
    "src/fdr/hwlm/hwlm.h": f"{HYPERSCAN_SRC}/hwlm/hwlm.h",
    "src/fdr/hwlm/hwlm_build.h": f"{HYPERSCAN_SRC}/hwlm/hwlm_build.h",
    "src/fdr/hwlm/hwlm_build.cpp": f"{HYPERSCAN_SRC}/hwlm/hwlm_build.cpp",
    "src/fdr/hwlm/hwlm_internal.h": f"{HYPERSCAN_SRC}/hwlm/hwlm_internal.h",
    "src/fdr/hwlm/hwlm_literal.h": f"{HYPERSCAN_SRC}/hwlm/hwlm_literal.h",
    "src/fdr/hwlm/hwlm_literal.cpp": f"{HYPERSCAN_SRC}/hwlm/hwlm_literal.cpp",
    "src/fdr/hwlm/noodle_engine.h": f"{HYPERSCAN_SRC}/hwlm/noodle_engine.h",
    "src/fdr/hwlm/noodle_build.h": f"{HYPERSCAN_SRC}/hwlm/noodle_build.h",
    "src/fdr/hwlm/noodle_build.cpp": f"{HYPERSCAN_SRC}/hwlm/noodle_build.cpp",
    "src/fdr/hwlm/noodle_internal.h": f"{HYPERSCAN_SRC}/hwlm/noodle_internal.h",
    
    # NFA files
    "src/fdr/nfa/nfa_api.h": f"{HYPERSCAN_SRC}/nfa/nfa_api.h",
    "src/fdr/nfa/nfa_api_queue.h": f"{HYPERSCAN_SRC}/nfa/nfa_api_queue.h",
    "src/fdr/nfa/nfa_internal.h": f"{HYPERSCAN_SRC}/nfa/nfa_internal.h",
    "src/fdr/nfa/nfa_kind.h": f"{HYPERSCAN_SRC}/nfa/nfa_kind.h",
    "src/fdr/nfa/accel.h": f"{HYPERSCAN_SRC}/nfa/accel.h",
    "src/fdr/nfa/callback.h": f"{HYPERSCAN_SRC}/nfa/callback.h",
    
    # SOM files
    "src/fdr/som/som.h": f"{HYPERSCAN_SRC}/som/som.h",
    
    # ROSE engine files
    "src/fdr/rose/rose_graph.h": f"{HYPERSCAN_SRC}/rose/rose_graph.h",
    "src/fdr/rose/rose_build.h": f"{HYPERSCAN_SRC}/rose/rose_build.h",
    "src/fdr/rose/rose_types.h": f"{HYPERSCAN_SRC}/rose/rose_types.h",
    "src/fdr/rose/rose_internal.h": f"{HYPERSCAN_SRC}/rose/rose_internal.h",
    "src/fdr/rose/rose_common.h": f"{HYPERSCAN_SRC}/rose/rose_common.h",
    
    # Utility headers
    "src/fdr/util/arch.h": f"{HYPERSCAN_SRC}/util/arch.h",
    "src/fdr/util/bitutils.h": f"{HYPERSCAN_SRC}/util/bitutils.h",
    "src/fdr/util/compare.h": f"{HYPERSCAN_SRC}/util/compare.h",
    "src/fdr/util/intrinsics.h": f"{HYPERSCAN_SRC}/util/intrinsics.h",
    "src/fdr/util/join.h": f"{HYPERSCAN_SRC}/util/join.h",
    "src/fdr/util/masked_move.h": f"{HYPERSCAN_SRC}/util/masked_move.h",
    "src/fdr/util/multibit.h": f"{HYPERSCAN_SRC}/util/multibit.h",
    "src/fdr/util/multibit.c": f"{HYPERSCAN_SRC}/util/multibit.c",
    "src/fdr/util/multibit_internal.h": f"{HYPERSCAN_SRC}/util/multibit_internal.h",
    "src/fdr/util/partial_store.h": f"{HYPERSCAN_SRC}/util/partial_store.h",
    "src/fdr/util/popcount.h": f"{HYPERSCAN_SRC}/util/popcount.h",
    "src/fdr/util/simd_types.h": f"{HYPERSCAN_SRC}/util/simd_types.h",
    "src/fdr/util/simd_utils.h": f"{HYPERSCAN_SRC}/util/simd_utils.h",
    "src/fdr/util/simd_utils.c": f"{HYPERSCAN_SRC}/util/simd_utils.c",
    "src/fdr/util/unaligned.h": f"{HYPERSCAN_SRC}/util/unaligned.h",
    "src/fdr/util/uniform_ops.h": f"{HYPERSCAN_SRC}/util/uniform_ops.h",
    "src/fdr/util/container.h": f"{HYPERSCAN_SRC}/util/container.h",
    "src/fdr/util/dump_mask.h": f"{HYPERSCAN_SRC}/util/dump_mask.h",
    "src/fdr/util/make_unique.h": f"{HYPERSCAN_SRC}/util/make_unique.h",
    "src/fdr/util/math.h": f"{HYPERSCAN_SRC}/util/math.h",
    "src/fdr/util/noncopyable.h": f"{HYPERSCAN_SRC}/util/noncopyable.h",
    "src/fdr/util/target_info.h": f"{HYPERSCAN_SRC}/util/target_info.h",
    "src/fdr/util/target_info.cpp": f"{HYPERSCAN_SRC}/util/target_info.cpp",
    "src/fdr/util/ue2string.h": f"{HYPERSCAN_SRC}/util/ue2string.h",
    "src/fdr/util/ue2string.cpp": f"{HYPERSCAN_SRC}/util/ue2string.cpp",
    "src/fdr/util/verify_types.h": f"{HYPERSCAN_SRC}/util/verify_types.h",
    "src/fdr/util/operators.h": f"{HYPERSCAN_SRC}/util/operators.h",
    "src/fdr/util/order_check.h": f"{HYPERSCAN_SRC}/util/order_check.h",
    "src/fdr/util/compile_context.h": f"{HYPERSCAN_SRC}/util/compile_context.h",
    "src/fdr/util/compile_error.h": f"{HYPERSCAN_SRC}/util/compile_error.h",
    "src/fdr/util/compile_error.cpp": f"{HYPERSCAN_SRC}/util/compile_error.cpp",
    "src/fdr/util/alloc.h": f"{HYPERSCAN_SRC}/util/alloc.h",
    "src/fdr/util/alloc.cpp": f"{HYPERSCAN_SRC}/util/alloc.cpp",
    "src/fdr/util/report.h": f"{HYPERSCAN_SRC}/util/report.h",
    "src/fdr/util/fatbit.h": f"{HYPERSCAN_SRC}/util/fatbit.h",
    "src/fdr/util/bytecode_ptr.h": f"{HYPERSCAN_SRC}/util/bytecode_ptr.h",
    "src/fdr/util/charreach.h": f"{HYPERSCAN_SRC}/util/charreach.h",
    "src/fdr/util/charreach.cpp": f"{HYPERSCAN_SRC}/util/charreach.cpp",
    "src/fdr/util/charreach_util.h": f"{HYPERSCAN_SRC}/util/charreach_util.h",
    "src/fdr/util/depth.h": f"{HYPERSCAN_SRC}/util/depth.h",
    "src/fdr/util/ue2_graph.h": f"{HYPERSCAN_SRC}/util/ue2_graph.h",
    "src/fdr/util/graph.h": f"{HYPERSCAN_SRC}/util/graph.h",
    "src/fdr/util/hash.h": f"{HYPERSCAN_SRC}/util/hash.h",
    "src/fdr/util/flat_containers.h": f"{HYPERSCAN_SRC}/util/flat_containers.h",
    "src/fdr/util/boundary_reports.h": f"{HYPERSCAN_SRC}/util/boundary_reports.h",
    "src/fdr/util/bitfield.h": f"{HYPERSCAN_SRC}/util/bitfield.h",
    "src/fdr/util/small_vector.h": f"{HYPERSCAN_SRC}/util/small_vector.h",
    "src/fdr/util/hash_dynamic_bitset.h": f"{HYPERSCAN_SRC}/util/hash_dynamic_bitset.h",
    "src/fdr/util/cpuid_flags.h": f"{HYPERSCAN_SRC}/util/cpuid_flags.h",
    "src/fdr/util/cpuid_flags.c": f"{HYPERSCAN_SRC}/util/cpuid_flags.c",
    
    # Parser files (needed by hwlm_build.cpp)
    "src/fdr/parser/position.h": f"{HYPERSCAN_SRC}/parser/position.h",
    "src/fdr/parser/position_info.h": f"{HYPERSCAN_SRC}/parser/position_info.h",
    "src/fdr/util/cpuid_inline.h": f"{HYPERSCAN_SRC}/util/cpuid_inline.h",
    "src/fdr/util/scatter.h": f"{HYPERSCAN_SRC}/util/scatter.h",
}


def download_fdr(base_dir="."):
    """Download FDR files from Hyperscan repository."""
    print("=" * 70)
    print("FDR String Matcher Setup")
    print("=" * 70)
    print(f"\nDownloading {len(FDR_FILES)} files from Hyperscan repository...")
    print()
    
    base_path = Path(base_dir)
    success_count = 0
    failed_files = []
    total_files = len(FDR_FILES)
    
    for idx, (dest_path, url) in enumerate(FDR_FILES.items(), 1):
        print(f"[{idx}/{total_files}] {dest_path} ... ", end="", flush=True)
        
        dest_file = base_path / dest_path
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            urllib.request.urlretrieve(url, dest_file)
            print("OK")
            success_count += 1
        except Exception as e:
            print(f"FAILED ({e})")
            failed_files.append(dest_path)
    
    print()
    print(f"Downloaded: {success_count}/{total_files} files")
    
    if failed_files:
        print(f"\nFailed to download {len(failed_files)} files:")
        for f in failed_files:
            print(f"  - {f}")
        return False
    
    return True
