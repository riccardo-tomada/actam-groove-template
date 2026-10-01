from math import exp
from random import random

def vca(wave, envelope):
    return list(x * y for x, y in zip(wave, envelope))
    
def noise(duration, sr = 48000):
    n = round(duration * sr)
    return [random() for _ in range(n)]

def exp_envelope(duration, decay_speed, sr= 48000):
    n = round(duration * sr)
    return [exp(-i*decay_speed) for i in range(n)]

def hihat(open_close, duration = 0.1):
    closed_dur = duration
    open_dur = duration * 8

    #funzione unica in cui specificare se open Hihat o Closed Hihat
    
    match open_close:
        case 'closed':
            return vca(noise(closed_dur), exp_envelope(closed_dur, 0.001))
        case 'open':
            return vca(noise(open_dur), exp_envelope(open_dur, 0.00025))

def square_wave_f_array(f,
                duration = 0.125,
                sr = 48000,
                amp = 0.5):
    n_samples = round(duration*sr)
    
    wave=[]
    i = 0

    while i < n_samples and i < len(f):

        if f[i] < 20: f[i] = 20
        period_samples = sr/f[i]
        period_samp_half = round(period_samples/2)

        wave += [-amp] * period_samp_half + [amp] * period_samp_half

        i = i + (period_samp_half*2)
    #somma periodo dopo periodo limitando la frequenza a 20 Hz per evitare periodi troppo lunghi

    return wave  

def kick(f = 1000, amp_decay = 0.0002, f_decay = 0.003, duration = 0.2, sr = 48000): #funzione kick con parametri: frequenza di partenza, decay del volume, decay della frequenza
    n_samples = round(duration*sr)
    f_arr = [f * exp(-i*f_decay) for i in range(n_samples)]

    osc = square_wave_f_array(f_arr, duration, sr)

    kick = vca(osc, exp_envelope(duration, amp_decay, sr))

    return kick

def mix(wave1, wave2, lev1 = 1.0, lev2 = 1.0):
    mix = [((x * lev1) + (y * lev2)) * .5 for x, y in zip(wave1, wave2)]
    return mix


def snare(f = 220, amp_decay = 0.00065, f_decay= 0.0001, duration = 0.2, sr = 48000):
    n_samples = round(duration*sr)
    f_arr = [f * exp(-i*f_decay) for i in range(n_samples)]
    top = square_wave_f_array(f_arr, duration, sr)

    bottom = noise(duration, sr)

    snare = mix(top, bottom, 0.9, 1)

    snare = vca(snare, exp_envelope(duration, amp_decay,sr))

    return snare


def pause(duration, sr = 48000): #funzione silence wave
    return [0] * round(duration * sr)

def fit_4(wave, note_length, bpm = 120, sr = 48000):
    """
    Funzione per fittare un segnale wave nella durata specificata come note_length
    in 16esimi, al bpm specificato
    """
    #note_length in sixteenths
    sixteenth_duration = 60/(bpm*4)
    duration = note_length * sixteenth_duration
    n_samples = round(duration*sr)

    padding = max(0, n_samples - len(wave))
    return wave[:n_samples] + [0] * padding

def fit_3(wave, note_length, bpm = 120, sr = 48000):
    """
    Stesso funzionamento di fit_4 ma su ritmi ternari
    """
    #note_length in sixteenth note triplets
    triplet_duration = 60/(bpm*6)
    duration = note_length * triplet_duration
    n_samples = round(duration*sr)

    padding = max(0, n_samples - len(wave))
    return wave[:n_samples] + [0] * padding

def swing(sample1, sample2, base = 16, ammount = 0.6, bpm = 120, sr = 48000):
    """
    unisce due sample calcolando la durata di ciascuno per ottenere una coppia
    di sedicesimi (o altro se base viene cambiata) swingati di ammount
    """
    pair_duration = 60/(bpm * (base/8))

    first_duration = pair_duration*ammount
    second_duration = pair_duration*(1-ammount)

    first_n_samples = round(first_duration*sr)
    second_n_samples = round(second_duration*sr)

    padding_1 = max(0, first_n_samples - len(sample1))
    first = sample1[:first_n_samples] + [0] * padding_1

    padding_2 = max(0, second_n_samples - len(sample2))
    second = sample2[:second_n_samples] + [0] * padding_2

    return first + second

def parse(pattern):
    parsed_pattern = []
    for c in pattern:
        if c == "x":
            parsed_pattern.append(1)
        elif c == ".":
            parsed_pattern.append(0)
    return parsed_pattern

def render_pattern_4(pattern, sample, base = 8, bpm = 120, sr = 48000):
    beat_list = [fit_4(sample, 16/base, bpm, sr) if n == 1 else fit_4(pause(10), 16/base, bpm, sr) for n in parse(pattern)]
    beat = []
    for i in range(len(beat_list)):
        beat += beat_list[i]
    return beat

def fit(wave, n_samples, sr = 48000):
    padding = max(0, n_samples - len(wave))
    return wave[:n_samples] + [0] * padding


def mixer(waves):
    tot_len = max([len(w) for w in waves])
    result = fit([], tot_len)

    for w in waves:
        repeats = round(tot_len/len(w))
        result = mix(w*repeats, result)

    return result