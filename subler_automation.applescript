function convertFileToMp4(inputFilePath, outputFolderPath) {
    const outputFilePath = outputFolderPath + "/" + inputFilePath.split("/").pop().replace(".mkv", ".mp4");
    const subler = Application("Subler");
    console.log(`Opening ${inputFilePath} in Subler...`);
    subler.open(inputFilePath);

}

function listFilePaths(folderPath, extension) {
    const folder = Application('System Events').folders.byName(folderPath);
    const files = folder.files.name();
    const subfolders = folder.folders.name();
    let allFiles = files.filter(file => file.endsWith(extension)).map(file => `${folderPath}/${file}`);
    subfolders.forEach(subfolder => {
        const subfolderPath = `${folderPath}/${subfolder}`;
        allFiles = allFiles.concat(listFilePaths(subfolderPath, extension));
    });
    return allFiles.sort();
}

function getFilesToConvert(mkvFiles, mp4Files) {
    return mkvFiles.filter(mkvFile => {
        const mp4File = mkvFile.replace(".mkv", ".mp4");
        return !mp4Files.includes(mp4File);
    });
}

function pathExists(path) {
    return Application('System Events').folders.byName(path).exists();
}

// Main Execution
function run(argv) {

    // Check if folder path was passed as argument
    if (argv.length != 1) {
        console.log("Please provide the absolute folder path as the one and only argument.");
        return;
    }
    folderPath = argv[0];
    if (folderPath.endsWith("/")) {
        folderPath = folderPath.slice(0, -1);
    }

    // Check if folder path is valid
    if (!pathExists(folderPath)) {
        console.log("The folder path provided is invalid.");
        return;
    }

    const mkvFolderPath = folderPath + "/mkv";
	const mp4FolderPath = folderPath + "/mp4";

    // Get list of files in both folders
    const mkvFiles = listFilePaths(mkvFolderPath, ".mkv");
    const mp4Files = listFilePaths(mp4FolderPath, ".mp4");

    // Get only mkv files which are not in mp4 folder
    const filesToConvert = getFilesToConvert(mkvFiles, mp4Files);

    // Open first file in Subler
    convertFileToMp4(filesToConvert[0], mp4FolderPath);

    console.log("the end");
}
