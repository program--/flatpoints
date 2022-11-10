class Header:
    start_of_data: int = -1
    coordinates_count: int = -1
    properties_count: int = -1
    properties_names: list[str] = []
    properties_types: list[int] = []
    offsets: list[int] = []

    def __init__(self, filepath: str = ""):
        if (filepath != ""):
            self.read(filepath)

    def __str__(self):
        return f'''--------- FLATPOINTS ---------
{self.coordinates_count} Coordinates
{self.properties_count} Properties {self.properties_names.__str__()[:30]}...
- METADATA:
    * SOD: {self.start_of_data}
    * Offsets: {self.offsets}
    * Types: {self.properties_types.__str__()[:30]}...
------------------------------'''

    def read(self, filepath: str):
        with open(filepath, 'rb') as file:
            magic = file.read(3).decode('utf-8')
            if (magic != 'FPS'):
                raise Exception(f"{filepath} is not a .flatpoints file.")

            self.start_of_data = int.from_bytes(
                file.read(8), 'little', signed=False)
            self.coordinates_count = int.from_bytes(
                file.read(8), 'little', signed=False)
            self.properties_count = int.from_bytes(
                file.read(8), 'little', signed=False)

            self.offsets = [int.from_bytes(file.read(
                8), 'little', signed=False) for _ in range(self.properties_count + 1)]
            self.properties_types = [int.from_bytes(
                file.read(1), 'little', signed=False) for _ in range(self.properties_count)]

            self.properties_names = []
            nulls = 0
            while nulls != self.properties_count:
                c = file.read(1).decode('utf-8')
                nulls += 1 if c == chr(0) else 0
                self.properties_names.append(c)
            self.properties_names = "".join(
                self.properties_names).split(chr(0))

            self.properties_names.pop()

    def write(self, filepath: str) -> int:
        bytes_written = 0

        with open(filepath, 'wb') as file:
            bytes_written += file.write(b'FPS')

            bytes_written += file.write(self.start_of_data.to_bytes(8,
                                        'little', signed=False))
            bytes_written += file.write(self.coordinates_count.to_bytes(
                8, 'little', signed=False))
            bytes_written += file.write(self.properties_count.to_bytes(
                8, 'little', signed=False))

            for offset in self.offsets:
                bytes_written += file.write(offset.to_bytes(8, 'little'))

            for ptype in self.properties_types:
                bytes_written += file.write(ptype.to_bytes(1, 'little'))

            for name in self.properties_names:
                bytes_written += file.write(f'{name}\0'.encode())

        return bytes_written
