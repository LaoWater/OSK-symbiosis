import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, FancyArrow

fig, ax = plt.subplots(figsize=(10, 6))

# Draw RNN over 3 time steps
for t in range(3):
    # Hidden state (circle)
    ax.add_patch(Circle((t*3, 2), 0.5, fill=False, color='blue'))
    # Input (rectangle below)
    ax.add_patch(Rectangle((t*3 - 0.5, 0), 1, 1, fill=False, color='green'))
    # Output (rectangle above)
    ax.add_patch(Rectangle((t*3 - 0.5, 3), 1, 1, fill=False, color='red'))
    # Arrows: input -> hidden, hidden -> output, hidden -> next hidden
    ax.add_patch(FancyArrow(t*3, 1, 0, 1, width=0.05, head_width=0.2, color='green'))
    ax.add_patch(FancyArrow(t*3, 2.5, 0, 0.5, width=0.05, head_width=0.2, color='red'))
    if t < 2:
        ax.add_patch(FancyArrow(t*3 + 0.5, 2, 2, 0, width=0.05, head_width=0.2, color='blue'))

# Add labels
for t in range(3):
    ax.text(t*3, 0.5, f'Input\nt={t}', ha='center', va='center', color='green')
    ax.text(t*3, 2, f'h_{t}', ha='center', va='center', color='blue')
    ax.text(t*3, 3.5, f'Output\nt={t}', ha='center', va='center', color='red')

ax.set_xlim(-1, 8)
ax.set_ylim(-1, 4.5)
ax.axis('off')
plt.title('Schematic of an RNN Language Model', pad=20)
plt.tight_layout()
plt.savefig('rnn_visualization.png', dpi=300)
plt.show()