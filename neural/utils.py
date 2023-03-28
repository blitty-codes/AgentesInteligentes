import tensorflow as tf
import matplotlib.pyplot as plt


def tokenize_and_add_padding(words, tokenizer, max_sequence_length):
    tokenizer.fit_on_texts(words)
    sequences = tokenizer.texts_to_sequences(words)
    word_index = tokenizer.word_index

    data = tf.keras.preprocessing.sequence.pad_sequences(
        sequences,
        value=0,
        maxlen=max_sequence_length
    )

    return sequences, word_index, data


def plot_history(history):
    plt.subplot(1, 2, 1)
    plt.plot(history.history['loss'], label='Training')
    plt.plot(history.history['val_loss'], label='Validation')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title(f'Training: {history.history["loss"][-1]:.2f}, validation: {history.history["val_loss"][-1]:.2f}')
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(history.history['accuracy'], label='Training')
    plt.plot(history.history['val_accuracy'], label='Validation')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.title(f'Training: {history.history["accuracy"][-1]:.2f}, validation: {history.history["val_accuracy"][-1]:.2f}')
    plt.legend()

    plt.show()
