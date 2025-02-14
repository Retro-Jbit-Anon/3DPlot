import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import re

st.title("3D Hexadecimal to Decimal Visualization")

# Function to convert hexadecimal to decimal
def hex_to_decimal(hex_str):
    is_negative = False
    if hex_str.startswith('-'):
        is_negative = True
        hex_str = hex_str[1:]  # Remove the negative sign

    if '.' in hex_str:
        integer_part, fractional_part = hex_str.split('.')
    else:
        integer_part, fractional_part = hex_str, ''

    decimal_int = int(integer_part, 16) if integer_part else 0
    decimal_fraction = sum(int(digit, 16) / (16 ** (i + 1)) for i, digit in enumerate(fractional_part))
    decimal_value = decimal_int + decimal_fraction
    return -decimal_value if is_negative else decimal_value

# File uploader for the Hex file
uploaded_file = st.file_uploader("Upload a HEX file", type=["hex"])

if uploaded_file is not None:
    # Read hex file and convert to decimal
    data = []
    for line in uploaded_file:
        line = line.decode("utf-8").strip()  # Decode bytes to string
        hex_values = re.findall(r'[0-9A-Fa-f.-]+', line)
        decimal_values = [hex_to_decimal(hv) for hv in hex_values]
        data.append(decimal_values)

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Check if the CSV has at least 10 columns
    if df.shape[1] < 10:
        st.error("The file must have at least 10 columns after conversion.")
    else:
        # Column selection for X, Y, Z
        columns = df.columns[:10]  # First 10 columns
        x_col = st.selectbox("Select X-axis column", columns)
        y_col = st.selectbox("Select Y-axis column", columns)
        z_col = st.selectbox("Select Z-axis column", columns)

        # Limit selection
        max_limit = len(df)
        limit_options = list(range(10, max_limit + 1, 10))
        limit = st.selectbox("Select number of values to read", limit_options, index=len(limit_options) - 1)

        # Filter the data
        df = df.iloc[:limit]

        # Extract selected columns
        X = df[x_col].values
        Y = df[y_col].values
        Z = df[z_col].values

        # Create a meshgrid for smooth plotting
        X_mesh, Y_mesh = np.meshgrid(np.linspace(X.min(), X.max(), len(X)), 
                                     np.linspace(Y.min(), Y.max(), len(Y)))
        Z_mesh = np.interp(X_mesh, X, Z)

        # Find peak and foot points
        max_idx = np.unravel_index(np.argmax(Z_mesh, axis=None), Z_mesh.shape)
        min_idx = np.unravel_index(np.argmin(Z_mesh, axis=None), Z_mesh.shape)

        peak_x, peak_y, peak_z = X_mesh[max_idx], Y_mesh[max_idx], Z_mesh[max_idx]
        foot_x, foot_y, foot_z = X_mesh[min_idx], Y_mesh[min_idx], Z_mesh[min_idx]

        # Plot using Plotly
        fig = go.Figure()

        # Surface plot with color gradient
        fig.add_trace(go.Surface(z=Z_mesh, x=X_mesh, y=Y_mesh, colorscale="Viridis"))

        # Peak point (Red)
        fig.add_trace(go.Scatter3d(
            x=[peak_x], y=[peak_y], z=[peak_z],
            mode="markers",
            marker=dict(size=6, color="red", symbol="diamond"),
            name="Peak"
        ))

        # Foot point (Blue)
        fig.add_trace(go.Scatter3d(
            x=[foot_x], y=[foot_y], z=[foot_z],
            mode="markers",
            marker=dict(size=6, color="blue", symbol="circle"),
            name="Foot"
        ))

        # Layout settings
        fig.update_layout(
            title="Hexadecimal Data 3D Visualization",
            scene=dict(
                xaxis_title=f"Column {x_col}",
                yaxis_title=f"Column {y_col}",
                zaxis_title=f"Column {z_col}"
            )
        )

        st.plotly_chart(fig)
