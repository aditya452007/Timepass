import os
import random
import string
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
from bloom_filter_core import BloomFilter

def generate_random_names(count, prefix="user"):
    """Auto-generates dummy usernames"""
    names = []
    for _ in range(count):
        # 6-character random suffix to guarantee uniqueness
        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        names.append(f"{prefix}_{suffix}")
    return names

def run_simulation():
    print("🚀 Starting Bloom Filter Simulation...")
    results = []

    # Our Simulation Map
    # Tuple: (Pool Size of users to insert, List of Bucket Sizes to test)
    phases = [
        (100, range(10, 51, 5)),       # Phase 1: Small pool, extremely constrained buckets
        (500, range(50, 101, 10)),     # Phase 2: Medium pool, small buckets
        (1000, range(100, 1001, 100))  # Phase 3: Large pool, massively scaled buckets
    ]

    hash_count = 3       # Fixed to 3 hash functions
    test_size = 500      # Number of exact new, unknown users to ping the filter with to test FPs

    for pool_size, bucket_sizes in phases:
        print(f"--> Simulating Phase: Pool Size = {pool_size}")
        # Generating fake DB data
        users = generate_random_names(pool_size, "taken")
        test_users = generate_random_names(test_size, "new_avail")

        for b_size in bucket_sizes:
            bf = BloomFilter(bucket_size=b_size, hash_count=hash_count)

            # Mass insert our initial user pool
            for u in users:
                bf.add_username(u)

            # Test false positives against users we KNOW were never inserted
            false_positives = 0
            for tu in test_users:
                if bf.check_username(tu):
                    false_positives += 1

            fp_rate = (false_positives / test_size) * 100

            results.append({
                "Pool Size": pool_size,
                "Bucket Size": b_size,
                "Actual Insertions": bf.actual_insertions,
                "Hash Collisions": bf.hash_collisions,
                "False Positive Rate (%)": fp_rate
            })

    # Convert tracked data to Dataframe
    df = pd.DataFrame(results)

    # ==========================================
    # Phase A: CYBERPUNK PLOTTING
    # ==========================================
    print("🎨 Generating Neon Cyberpunk Visualizations...")
    plt.style.use("dark_background")
    
    # Absolute Cyberpunk Colors
    neon_cyan = "#08F7FE"
    neon_magenta = "#FE53BB"
    neon_yellow = "#F5D300"
    deep_bg = "#0A0A10"

    # 1. Line Plot
    plt.figure(figsize=(10, 6))
    ax = plt.gca()
    ax.set_facecolor(deep_bg)
    plt.gcf().patch.set_facecolor(deep_bg)

    sns.lineplot(
        data=df, x="Bucket Size", y="False Positive Rate (%)",
        hue="Pool Size", palette=[neon_cyan, neon_magenta, neon_yellow],
        linewidth=3.5, marker="D", markersize=8
    )

    plt.title("False Positive Rate vs. Bucket Architecture", color="white", fontsize=18, pad=15)
    plt.grid(color="#2A3459", linestyle="--", linewidth=0.5, alpha=0.5)
    plt.setp(ax.get_xticklabels(), color="#08F7FE")
    plt.setp(ax.get_yticklabels(), color="#FE53BB")
    plt.tight_layout()
    plt.savefig("fp_line_plot.png", facecolor=deep_bg, dpi=300)
    plt.close()

    # 2. Heatmap Matrix
    plt.figure(figsize=(10, 6))
    ax = plt.gca()
    ax.set_facecolor(deep_bg)
    plt.gcf().patch.set_facecolor(deep_bg)

    pivot_df = df.pivot_table(index="Pool Size", columns="Bucket Size", values="False Positive Rate (%)")
    
    # We use magma theme since it aligns well with dark neon designs
    sns.heatmap(
        pivot_df, cmap="magma", annot=False, 
        cbar_kws={'label': 'False Positive Rate (%)'}
    )
    plt.title("Heatmap: Hash Collision Saturation", color="white", fontsize=18, pad=15)
    plt.tight_layout()
    plt.savefig("fp_heatmap.png", facecolor=deep_bg, dpi=300)
    plt.close()

    # ==========================================
    # Phase B: PDF REPORT GENERATION 
    # ==========================================
    print("📄 Compiling Highly Detailed, Visual PDF Report...")
    class BloomPDF(FPDF):
        def footer(self):
            self.set_y(-15)
            self.set_font('helvetica', 'I', 8)
            self.cell(0, 10, f'Page {self.page_no()}', align='C', ln=True)

    def draw_bit_matrix(pdf, bit_array, highlight_indices=None):
        if highlight_indices is None:
            highlight_indices = []
        cell_w = 190 / len(bit_array)
        if cell_w > 12: cell_w = 12
        pdf.set_font("helvetica", "B", 12)
        total_w = cell_w * len(bit_array)
        start_x = (210 - total_w) / 2
        pdf.set_x(start_x)
        for i, bit in enumerate(bit_array):
            if i in highlight_indices:
                pdf.set_fill_color(100, 255, 100) # Green
                pdf.set_text_color(0, 0, 0)
            elif bit == 1:
                pdf.set_fill_color(200, 200, 200) # Gray
                pdf.set_text_color(0, 0, 0)
            else:
                pdf.set_fill_color(255, 255, 255) # White
                pdf.set_text_color(200, 200, 200)
            pdf.cell(cell_w, 10, str(bit), border=1, align='C', fill=True)
        pdf.ln(13)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("helvetica", "", 12)

    pdf = BloomPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Title
    pdf.set_font("helvetica", "B", 24)
    pdf.cell(0, 20, "Bloom Filters: A Visual Guide", align='C', ln=True)
    pdf.ln(5)

    # Section 1: The Bottleneck Problem
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, "1. The Database Search Bottleneck", ln=True)
    pdf.set_font("helvetica", "", 12)
    pdf.multi_cell(0, 8, txt=(
        "When millions of users sign up for a service, checking if a username is already taken becomes a massive bottleneck. "
        "A traditional database has to scan its massive index (O(N) or O(log N) time) for every single keystroke the user types. "
        "This causes high latency, sluggish UI, and massive server costs."
    ))
    pdf.ln(5)

    # Section 2: Enter the Bloom Filter
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, "2. Enter the Bloom Filter (The Bucket Matrix)", ln=True)
    pdf.set_font("helvetica", "", 12)
    pdf.multi_cell(0, 8, txt=(
        "A Bloom Filter solves this by sacrificing absolute certainty for extreme speed and memory efficiency. "
        "Imagine an array of empty buckets (representing bits initialized to 0). "
        "When a user signs up, we pass their name through 3 different mathematical hash functions. "
        "These give us 3 random (but consistent!) numbers, acting as indices. We flip the bits at these buckets to 1. "
        "Let's simulate this with a small 15-bucket filter."
    ))
    pdf.ln(5)

    # Mini simulation for visual
    bf_mini = BloomFilter(bucket_size=15, hash_count=3)
    
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 8, "Initial Empty Matrix (0 Users)", ln=True)
    pdf.set_font("helvetica", "", 12)
    draw_bit_matrix(pdf, bf_mini.bit_array)

    user1 = "alice"
    idx1 = bf_mini._get_hash_indices(user1)
    bf_mini.add_username(user1)
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 8, f"Action: User '{user1}' signs up.", ln=True)
    pdf.set_font("helvetica", "", 12)
    pdf.multi_cell(0, 8, txt=f"Hash functions calculate indices: {idx1}. We flip these to 1 (highlighted in Green).")
    draw_bit_matrix(pdf, bf_mini.bit_array, highlight_indices=idx1)

    user2 = "bob"
    idx2 = bf_mini._get_hash_indices(user2)
    bf_mini.add_username(user2)
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 8, f"Action: User '{user2}' signs up.", ln=True)
    pdf.set_font("helvetica", "", 12)
    pdf.multi_cell(0, 8, txt=f"Hash functions calculate indices: {idx2}. We flip these to 1.")
    draw_bit_matrix(pdf, bf_mini.bit_array, highlight_indices=idx2)
    
    pdf.ln(3)

    # Section 3: Checking Availability
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, "3. Checking if a Username is Taken", ln=True)
    pdf.set_font("helvetica", "", 12)
    
    test_avail = "dave"
    idx_avail = bf_mini._get_hash_indices(test_avail)
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 8, f"Action: Checking available user '{test_avail}'", ln=True)
    pdf.set_font("helvetica", "", 12)
    pdf.multi_cell(0, 8, txt=f"Hashes for '{test_avail}' land on {idx_avail}. Because the matrix has a '0' in at least one of these spots, it's physically impossible for '{test_avail}' to have ever signed up! The name is 100% DEFINITELY AVAILABLE.")
    pdf.ln(5)

    # Section 4: The False Positive
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, "4. The Phantom Collision: False Positives", ln=True)
    pdf.set_font("helvetica", "", 12)
    pdf.multi_cell(0, 8, txt=(
        "Because our matrix has a limited number of buckets (15 here), as more users sign up, more and more bits turn to 1. "
        "Eventually, a completely new user might roll hash indices that were already independently flipped to 1 by a combination of other users. "
        "Let's find an identical collision."
    ))

    # Programmatically find FP
    fp_user = ""
    fp_idx = []
    i = 0
    while True:
        test = f"user_{i}"
        cur_idx = bf_mini._get_hash_indices(test)
        if test not in [user1, user2] and all(bf_mini.bit_array[x] == 1 for x in cur_idx):
            fp_user = test
            fp_idx = cur_idx
            break
        i += 1

    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 8, f"Action: User '{fp_user}' tries to sign up.", ln=True)
    pdf.set_font("helvetica", "", 12)
    pdf.multi_cell(0, 8, txt=f"'{fp_user}' has NEVER signed up. However, their hashes hit indices: {fp_idx}. "
                             f"Wait! Looking at the matrix, 'alice' and 'bob' already flipped all of these exact indices to 1. "
                             f"Since all buckets at {fp_idx} are 1, the filter screams 'TAKEN!'. This is a False Positive.")
    draw_bit_matrix(pdf, bf_mini.bit_array, highlight_indices=fp_idx)

    pdf.multi_cell(0, 8, txt="How do we fix this? We use a MUCH larger matrix (say, millions of bits) and more hash functions to dilute the density and exponentially reduce the chances of a phantom collision.")
    pdf.ln(10)

    # Setup New Page for Graphs
    pdf.add_page()
    
    # Section 5: Simulation Results
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, "5. Scale Testing: Simulation Results", ln=True)
    pdf.set_font("helvetica", "", 12)
    pdf.multi_cell(0, 8, txt=(
        "To test exactly how False Positives scale, we built a simulation up to 1000 users and varied the bucket array size up to 1000. "
        "Notice in the visualizations below how the False Positive rate plummets to near zero as the Bucket Size increases relative to the user pool."
    ))
    pdf.ln(5)
    
    # Insert Images
    pdf.image("fp_line_plot.png", x=10, w=190)
    pdf.ln(5)
    pdf.image("fp_heatmap.png", x=10, w=190)

    # Compile Final File
    report_name = "Bloom_Filter_Explained.pdf"
    pdf.output(report_name)
    print(f"✅ Success! Report fully generated as '{report_name}'.")

if __name__ == "__main__":
    run_simulation()
