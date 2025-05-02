namespace UIMeetMind.Models;

public class MeetingFile
{
    public string MeetingId { get; set; }

    /// <summary>
    /// Nom du fichier (ex: "recording_1234.wav")
    /// </summary>
    public string Title { get; set; } = string.Empty;

    /// <summary>
    /// Chemin complet ou URL pour le téléchargement
    /// </summary>
    public string FilePath { get; set; } = string.Empty;

    /// <summary>
    /// Date de création ou de génération du fichier
    /// </summary>
    public DateTime EndTimestamp { get; set; }

    /// <summary>
    /// Type de fichier: "audio", "transcript", "summary"
    /// </summary>
    public string Type { get; set; } = string.Empty;
}